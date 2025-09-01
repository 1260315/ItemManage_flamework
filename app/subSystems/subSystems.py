"""
subSystems/subSystems.py

備品情報管理システム。
備品情報データベースのテーブルを定義する
"""
from flask_sqlalchemy import SQLAlchemy
from flask import session
from datetime import datetime
from sqlalchemy.sql import func

db = SQLAlchemy()
# # 備品情報管理システム

# equipment_db に入れるモデル

# カテゴリーテーブル ==================================
class Categories(db.Model):
    __bind_key__ = 'item'   #備品情報データベースにバインド
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)


# 備品情報テーブル   ==================================
class Items(db.Model):
    __bind_key__ = 'item'  #備品情報データベースにバインド
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10), unique=False, nullable=False)
    registrant_id = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.String(100))

    #登録された日時(自動的に現在日時を登録する)
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)

    
    #データを登録する
    #def register(self, id, name, category_id, registrant_id, date, remark):

    #idからデータの内容を参照する
    @classmethod
    def refer(cls, id):
        return cls.query.get(int(id)) 

    #備品編集情報伝送処理
    #データのidと編集内容を引数にとって、データベースの内容を変更する
    #@classmethod
    #def edit(cls, id, name, category_id, registrant_id, date, remark):

    #備品情報削除処理
    #削除するデータのidを受け取って、データを削除する
    #無事に削除できたら、削除したitemを返す。
    @classmethod
    def delete(cls, id):
        delete_item = cls.refer(id)
        if delete_item:
            db.session.delete(delete_item)
            db.session.commit()
            return delete_item
        else:
            return None

#中間テーブル       ==================================
class ItemCategory(db.Model):
    __bind_key__ = "item"
    __tablename__ = "item_category"

    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), primary_key=True)

# 多対多リレーション
Categories.items = db.relationship(
    "Items",                     # 対象となるモデル名（文字列 or クラス）
    secondary = ItemCategory.__table__,    # 多対多の場合に使う中間テーブル
    back_populates = "categories" # 相手側モデルで定義したリレーション名と対応付ける
)

Items.categories = db.relationship(
    "Categories",       # 対象となるモデル名（文字列 or クラス）
    secondary = ItemCategory.__table__,    # 多対多の場合に使う中間テーブル
    back_populates = "items"    # 相手側モデルで定義したリレーション名と対応付ける
)