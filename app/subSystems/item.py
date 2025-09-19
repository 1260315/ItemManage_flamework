"""
subSystems/item.py

備品情報管理システムを想定。
備品情報データベースのテーブルを定義する
"""
import mysql.connector
from flask import g

#エクスポート用
import io
import pandas as pd
import datetime
import re


def get_itemdb():
    if "item_db" not in g:
        g.item_db = mysql.connector.connect(
            host="db",
            user="root",
            password="password",
            database="item_db",
            charset="utf8mb4",
            autocommit=True
        )

    return g.item_db

def close_itemdb(e=None):   #e=Noneはなに？
    item_db = g.pop("item_db", None)
    if item_db is not None:
        item_db.close()

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

        return item_id

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
    
    @classmethod
    def get_category_names(cls,item_id):
        db = get_itemdb()
        cursor = db.cursor()
        
        cursor.execute("""
        SELECT c.name
        FROM item_category ic
        JOIN categories c ON ic.category_id = c.id
        WHERE ic.item_id = %s
        """, (item_id,))

        # 結果取得
        category_names = [row[0] for row in cursor.fetchall()]

        # クローズ
        cursor.close()
        db.close()

        # カンマ区切りの文字列で返す
        return ", ".join(category_names)

    @classmethod
    def export_csv(cls):
        items = Item.get_all()

        for i in items : 
            created_at = i.get('created_at')
            if isinstance(created_at, datetime.datetime):
                i['created_at'] = created_at.strftime("%Y-%m-%d %H:%M:%S")
            elif created_at is None:
                i['created_at'] = ''

            #category_itemから
                i['categories'] = Item.get_category_names(i['id'])

        df = pd.DataFrame([{
            '備品ID': i['id'],
            '備品名': i['name'],
            '登録者': i['registrant_id'],
            '登録日':i['created_at'],
            '備考': i['remark']
        }for i in items])


        output = io.BytesIO()#空のメモリ上の文字列バッファを作成
        df.to_csv(output,index=False,encoding='utf-8-sig')
        output.seek(0)

        return output
    
    @classmethod
    def sort(cls, order, ses):
        allowed_columns = ['items.id','items.name','items.created_at','items.registrant_id','items.category_id']
        if order not in allowed_columns:
            order = 'items.id'
        elif ses['sortOrder'] == order:
            ses['sortDirection'] = not ses['sortDirection']
        else:
            ses['sortOrder'] = order
            ses['sortDirection'] = True
    
    @classmethod
    def addOR(cls, value, fieldName):
        if not value:
            return [], []
        conditions = []
        params = []
        orParts = []
        if isinstance(value, str):
            orParts = re.sub("[\u3000\t]", "", value).split("+")
            for orPart in orParts:
                andPart = [t for t in orPart.split() if t]
                if andPart:
                    conditions.append("(" + " and ".join([f"{fieldName} like %s" for _ in andPart]) + ")")
                    params.extend([f"%{x}%" for x in andPart])
        elif isinstance(value,(list,tuple)):
            if len(value) > 0:
                placeholders = ", ".join(["%s"] * len(value))
                conditions.append(f"exists ( select 1 from item_category where {fieldName} IN ({placeholders}) and items.id = item_category.item_id) ")
                params.extend(value)
        condition = " or ".join(conditions)
        return params, f" ({condition}) "
    
    @classmethod
    def search(cls, values, ses):
        commands=[]
        params=[]
        sql = """select items.id, any_value(items.name) as iname, any_value(items.created_at) as at, any_value(items.registrant_id) as reg,
            GROUP_CONCAT(categories.name) as category_names, any_value(items.remark)
            from items left join item_category on items.id = item_category.item_id 
            left join categories on item_category.category_id = categories.id"""
        for key, value in values:
            if key == "category_id":
                prelist, presql = cls.addOR(value, f"item_category.{key}")
            else:
                prelist, presql = cls.addOR(value, f"items.{key}")
            if prelist:
                commands.append(presql)
                params.extend(prelist)
        if commands:
            sql += " where " + " and ".join(commands)
        allowed_columns = ['items.id','items.name','items.created_at','items.registrant_id','items.category_id']
        order = ses['sortOrder'] if ses['sortOrder'] in allowed_columns  else 'items.id'
        dir = "asc" if ses['sortDirection'] else "desc"
        sql += f" group by items.id order by {order} {dir}"
        db = get_itemdb()
        cursor=db.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows
