"""
subSystems/subSystems.py

備品情報管理システム。
備品情報データベースのテーブルを定義する
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy

# class Auth(db.Model):
#     __bind_key__ = 'auth'   #会員情報データベースにバインド
#     id = db.Column(db.Integer, primary_key=True, autoincrement=False)
#     password = db.Column(db.String(256), nullable=False)
#     isActive = db.Column(db.Boolean, default=True)

#     def set_password(self, password):
#         self.password = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password, password)

# # 備品情報管理システム
# # equipment_db に入れるモデル
# class Item(db.Model):
#     __bind_key__ = 'Item'  #備品情報データベースにバインド
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(10), unique=False, nullable=False)
#     category_id = db.Column(db.Integer, nullable=False)
#     registrant_id = db.Column(db.Integer, nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     remark = db.Column(db.String(100))

#     #データを登録する
#     def register(self, id, name, category_id, registrant_id, date, remark):


#     #idからデータの内容を参照する
#     def refer(self, id):

#     #備品編集情報伝送処理
#     #データのidと編集内容を引数にとって、データベースの内容を変更する
#     def edit(self, id, name, category_id, registrant_id, date, remark):


#     #備品情報削除処理
#     #削除するデータのidを受け取って、データを削除する
#     def delete(self, id):


# # カテゴリーデータベース
# class Category(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(20), nullable=False)

    


#     #idから名前を参照
#     def id2name(self, id):