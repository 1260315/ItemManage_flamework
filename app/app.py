"""
app.py

共通受付システムを想定
エンドポイントへのルーティングを定義する
"""
import argparse

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
# from subSystems.subSystems import db, Auth, Item, Category

# Flaskアプリ初期化
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = "  "
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

# DB初期化
# db.init_app(app)    

###以下、エンドポイントへのルーティング
#===================================================================
@app.route('/')
def home():
    return "テスト"

#テスト用の検索ページ
#データベースに登録されているデータを全て一覧表示する画面を生成。
#編集ボタン・削除ボタンも合わせて生成して、それをクリックすると各業務に遷移する
@app.route('/test/')
def test():
    #環境テスト
    return render_template('test0.html')

    #equipments = db.session.query(Item.name, Item.category_id, Item.registrant_id, Item.date, Item.remark)
    #カテゴリーIDから、カテゴリーを参照する
#===================================================================
# #登録業務(テスト)
# @app.route('/register/', methods = ['GET', 'POST'])
# def register():
#     if request.method == 'GET':
#         return render_template("register.html")

#     elif request.method == 'POST':

#         return "登録完了"

# #===================================================================
# #編集業務
# @app.route('/edit/', methods = ['GET', 'POST'])
# def edit():
#     if request.method == 'GET':

#     elif request.method == 'POST':


# #===================================================================
# #削除業務
# @app.route('/delete/', methods = ['GET', 'POST'])
# def delete():
#     if request.method == 'GET':

#     elif request.method == 'POST':



### ===== アプリ実行 ===== ###
if __name__ == "__main__":

    app.run(debug=True,host="0.0.0.0", port=5000)

    # models.pyの定義に基づいてテーブルの作成(初回のみ)
    # with app.app_context():
    #     db.create_all()