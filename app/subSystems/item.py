"""
subSystems/item.py

備品情報管理システムを想定。
備品情報データベースのテーブルを定義する
"""
import mysql.connector
from flask import g,session
import pandas as pd
from pandas.errors import EmptyDataError
import csv

def get_itemdb():
    if "item_db" not in g:
        g.item_db = mysql.connector.connect(
            host="db",
            user="root",
            password="password",
            database="item_db",
            autocommit=True
        )
    print("item_dbとのコネクションを確立できました！")

    return g.item_db

def close_itemdb(e=None):   #e=Noneはなに？
    item_db = g.pop("item_db", None)
    if item_db is not None:
        item_db.close()

# def init_itemdb():
#     db = get_itemdb()
#     cursor = db.cursor()

#     # seed.sql を読み込む
#     with open("seed.sql", encoding="utf-8") as f:
#         sql_commands = f.read().split(";")

#     for command in sql_commands:
#         command = command.strip()
#         if command:
#             cursor.execute(command)

#     cursor.close()
    
#     close_itemdb()
#     print("DBを初期化しました")

#カテゴリーテーブルの操作========================================

class Category:
    @classmethod
    def get_all(cls):
        db = get_itemdb()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM categories")
        data = cursor.fetchall()
        cursor.close()
        return data

    @classmethod
    def get_by_id(cls, cid):
        db = get_itemdb()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM categories WHERE id=%s", (cid,))
        data = cursor.fetchone()
        cursor.close()
        return data

#備品情報テーブルの操作==========================================

class Item():

    @classmethod
    def get_all(cls):
        db = get_itemdb()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT i.id, i.name, i.remark, i.registrant_id, i.created_at,
            GROUP_CONCAT(c.id) AS category_ids,
            GROUP_CONCAT(c.name) AS category_names
            FROM items i
            LEFT JOIN item_category ic ON i.id = ic.item_id
            LEFT JOIN categories c ON ic.category_id = c.id
            GROUP BY i.id
        """)
        items = cursor.fetchall()

        # categoriesをリストに変換してテンプレートでmap(attribute='name')を使えるようにする
        for item in items:
            if item['category_ids']:
                ids = item['category_ids'].split(',')
                names = item['category_names'].split(',')
                item['categories'] = [{'id': int(cid), 'name': name} for cid, name in zip(ids, names)]
            else:
                item['categories'] = []

        cursor.close()
        return items

    @classmethod
    def refer(cls, id):
        db = get_itemdb()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT i.id, i.name, i.remark, i.registrant_id, i.created_at,
            GROUP_CONCAT(c.id) AS category_ids,
            GROUP_CONCAT(c.name) AS category_names
            FROM items i
            LEFT JOIN item_category ic ON i.id = ic.item_id
            LEFT JOIN categories c ON ic.category_id = c.id
            WHERE i.id = %s
            GROUP BY i.id
        """, (id,))
        item = cursor.fetchone()

        if item:
            if item['category_ids']:
                ids = item['category_ids'].split(',')
                names = item['category_names'].split(',')
                item['categories'] = [{'id': int(cid), 'name': name} for cid, name in zip(ids, names)]
            else:
                item['categories'] = []

        cursor.close()
        return item

    @classmethod
    def insert(cls, name, registrant_id, remark, category_ids):
        db = get_itemdb()
        cursor = db.cursor()

        # 1. items テーブルに登録
        cursor.execute(
            "INSERT INTO items (name, registrant_id, remark) VALUES (%s, %s, %s)",
            (name, registrant_id, remark)
        )
        item_id = cursor.lastrowid  # 新規登録された item の ID

        # 2. item_category テーブルに登録
        for cid in category_ids:
            cursor.execute(
                "INSERT INTO item_category (item_id, category_id) VALUES (%s, %s)",
                (item_id, cid)
            )

        cursor.close()
        db.commit()

        return 

    @classmethod
    def edit(cls, id, name, category_ids, remark):
        db = get_itemdb()
        cursor = db.cursor()

        # itemsテーブルを更新
        cursor.execute("""
            UPDATE items
            SET name=%s, remark=%s
            WHERE id=%s
        """, (name, remark, id))

        # item_category をいったん削除して再登録
        cursor.execute("DELETE FROM item_category WHERE item_id=%s", (id,))
        for cid in category_ids:
            cursor.execute("INSERT INTO item_category (item_id, category_id) VALUES (%s,%s)", (id, cid))

        cursor.close()
        db.commit()

        return cls.refer(id)

    @classmethod
    def delete(cls, id):
        db = get_itemdb()
        cursor = db.cursor()
        delete_item = cls.refer(id)
        if not delete_item:
            return None
        else:
            # 先に item_category を削除
            cursor.execute("DELETE FROM item_category WHERE item_id=%s", (id,))
            # items を削除
            cursor.execute("DELETE FROM items WHERE id=%s", (id,))
            cursor.close()
            db.commit()
            return delete_item
        
    #エラーがなければ空、エラーがあればエラーメッセージを辞書形式でいれて返す
    @classmethod
    def check(cls, name, remark):
        errors = {}     #空のエラーリストを作成

        if not name:
            errors["name"] = "備品名は必須項目です。"
        elif len(name) > 10:
            errors["name"] = "備品名は10文字以内で入力してください。"
        
        if len(remark) > 100:
            errors["remark"] = "備考は100文字以内で入力してください"
        
        return errors
    # TODO: ==========================================================================
    

    @classmethod
    def clear_all(cls):
        """備品データを全削除し、AUTO_INCREMENTをリセット"""
        db = get_itemdb()
        cursor = db.cursor()

        # 備品データを全削除
        cursor.execute("DELETE FROM item_category")
        cursor.execute("DELETE FROM items")

        # AUTO_INCREMENT(自動で連番を振る仕組み)をリセットし１から始める
        cursor.execute("ALTER TABLE item_category AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE items AUTO_INCREMENT = 1")

        db.commit()
        cursor.close()

    
    @classmethod
    def import_from_file(cls, filepath):
        if not filepath.endswith(".csv"):
            return False, "CSVファイルではありません"

        # 列数の一貫性チェック（csv.reader でクォートも正しく解釈）
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            lines = list(reader)

        if not lines:
            return False, "CSVファイルが空です"

        expected_cols = len(lines[0])  # ヘッダーの列数
        for row in lines[1:]:
            if len(row) != expected_cols:
                return False, "CSVに余分なカンマがあります"

        # pandasで読み込み
        try:
            df = pd.read_csv(filepath, encoding="utf-8")
        except EmptyDataError:
            return False, "CSVファイルが空です"

        if df.empty:
            return False, "CSVファイルにデータがありません"

        # カラムチェック（順序も含めて一致必須）
        required_cols = ["name", "remark", "category_ids"]
        if list(df.columns) != required_cols:
            return False, f"CSVのカラムが不正です。必須カラムは {required_cols} です。実際: {list(df.columns)}"

        db = get_itemdb()
        cursor = db.cursor()
        imported_items = []

        try:
            registrant_id = session.get("studentID")

            for _, row in df.iterrows():
                name = None if pd.isna(row['name']) else str(row['name']).strip()
                remark = None if pd.isna(row['remark']) else str(row['remark']).strip()
                category_raw = None if pd.isna(row['category_ids']) else str(row['category_ids']).strip()

                # 必須チェック
                if not name:
                    return False, "備品名(name) が空です"
                if not category_raw:
                    return False, "カテゴリ(category_ids) が空です"

                # 整数・範囲チェック
                try:
                    category_ids = [int(cid) for cid in category_raw.split(',')]
                except ValueError:
                    return False, f"カテゴリIDが整数ではありません: {category_raw}"

                for cid in category_ids:
                    if cid < 1 or cid > 6:
                        return False, f"カテゴリID {cid} が範囲外です (1〜6 のみ有効)"

                # items 登録
                cursor.execute(
                    "INSERT INTO items (name, registrant_id, remark) VALUES (%s, %s, %s)",
                    (name, registrant_id, remark)
                )
                item_id = cursor.lastrowid

                # categories 登録
                for cid in category_ids:
                    cursor.execute(
                        "INSERT INTO item_category (item_id, category_id) VALUES (%s, %s)",
                        (item_id, cid)
                    )

                imported_items.append({
                    "id": item_id,
                    "name": name,
                    "remark": remark,
                    "registrant_id": registrant_id,
                    "created_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "categories": category_ids
                })

            db.commit()
            cursor.close()
            return True, imported_items

        except Exception as e:
            db.rollback()
            cursor.close()
            return False, str(e)




