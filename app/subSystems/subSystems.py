"""
subSystems/subSystems.py

備品情報管理システム。
備品情報データベースのテーブルを定義する
"""
import mysql.connector
from flask import g

def get_itemdb():
    if "item_db" not in g:
        g.item_db = mysql.connector.connect(
            host="db",
            user="root",
            password="password",
            database="item_db",
            autocommit=True
        )

    return g.item_db

def close_itemdb(e=None):   #e=Noneはなに？
    item_db = g.pop("item_db", None)
    if item_db is not None:
        item_db.close()

def init_itemdb():
    db = get_itemdb()
    cursor = db.cursor()

    # seed.sql を読み込む
    with open("seed.sql", encoding="utf-8") as f:
        sql_commands = f.read().split(";")

    for command in sql_commands:
        command = command.strip()
        if command:
            cursor.execute(command)

    cursor.close()
    
    close_itemdb()
    print("DBを初期化しました")

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

    @classmethod
    def insert(cls, name):
        db = get_itemdb()
        cursor = db.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        cursor.close()
        return True

    @classmethod
    def delete(cls, cid):
        db = get_itemdb()
        cursor = db.cursor()
        cursor.execute("DELETE FROM categories WHERE id=%s", (cid,))
        cursor.close()
        return True


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


# from flask_sqlalchemy import SQLAlchemy
# from flask import session
# from datetime import datetime
# from sqlalchemy.sql import func

# db = SQLAlchemy()
# # # 備品情報管理システム

# # equipment_db に入れるモデル

# # カテゴリーテーブル ==================================
# class Categories(db.Model):
#     __bind_key__ = 'item'   #備品情報データベースにバインド
#     __tablename__ = "categories"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(20), nullable=False)


# # 備品情報テーブル   ==================================
# class Items(db.Model):
#     __bind_key__ = 'item'  #備品情報データベースにバインド
#     __tablename__ = "items"

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(10), unique=False, nullable=False)
#     registrant_id = db.Column(db.Integer, nullable=False)
#     remark = db.Column(db.String(100))

#     #登録された日時(自動的に現在日時を登録する)
#     created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    
#     #データを登録する
#     #def register(self, id, name, category_id, registrant_id, date, remark):

#     #idからデータの内容を参照する
#     @classmethod
#     def refer(cls, id):
#         return cls.query.get(id) 

#     #備品編集情報確認処理
#     #編集前と編集後に違いがあるか確認する処理
#     @classmethod
#     def check(cls, id, name, category_ids, remark):
#         bf_item = cls.query.get(id) 

#         #編集の前後のデータをdictに変換
#         #このとき、bfのカテゴリーをidでリストにする
#         # =>formでidのリストで入力されるため
#         bf_category_ids = [c.id for c in bf_item.categories]
#         bf_dict = {
#             "name": bf_item.name,
#             "category_ids": bf_category_ids,
#             "remark": bf_item.remark,
#         }

#         category_ids = [int(c_id) for c_id in category_ids]
#         af_dict = {
#             "name": name,
#             "category_ids": category_ids,
#             "remark": remark,
#         }

#         #値に違いがあるか検証
#         #違えば1, 違わなければNoneを返す
#         for key in ["name", "category_ids", "remark"]:
#             if bf_dict[key] != af_dict[key]:
#                 print(bf_dict[key])
#                 print(af_dict[key])
#                 return 1
#         return None


#     #備品編集情報伝送処理
#     #データのidと編集内容を引数にとって、データベースの内容を変更する
#     @classmethod
#     def edit(cls, id, name, category_ids, remark):
#         edit_item = cls.query.get(id)
#         edit_item.name = name
#         edit_item.remark = remark
        
#         #いったんcategoriesを空にする
#         edit_item.categories = []
#         for cid in category_ids:
#             category = db.session.get(Categories, cid)
#             if category:    # categoryがNULLじゃなければ
#                 edit_item.categories.append(category)

#         db.session.commit() 

#         return edit_item


#     #備品情報削除処理
#     #削除するデータのidを受け取って、データを削除する
#     #無事に削除できたら、削除したitemを返す。
#     @classmethod
#     def delete(cls, id):
#         delete_item = cls.refer(id)
#         if delete_item:
#             db.session.delete(delete_item)
#             db.session.commit()
#             return delete_item
#         else:
#             return None

# #中間テーブル       ==================================
# class ItemCategory(db.Model):
#     __bind_key__ = "item"
#     __tablename__ = "item_category"

#     item_id = db.Column(db.Integer, db.ForeignKey("items.id"), primary_key=True)
#     category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), primary_key=True)

# # 多対多リレーション
# Categories.items = db.relationship(
#     "Items",                     # 対象となるモデル名（文字列 or クラス）
#     secondary = ItemCategory.__table__,    # 多対多の場合に使う中間テーブル
#     back_populates = "categories" # 相手側モデルで定義したリレーション名と対応付ける
# )

# Items.categories = db.relationship(
#     "Categories",       # 対象となるモデル名（文字列 or クラス）
#     secondary = ItemCategory.__table__,    # 多対多の場合に使う中間テーブル
#     back_populates = "items"    # 相手側モデルで定義したリレーション名と対応付ける
# )