"""
app.py

共通受付システムを想定
エンドポイントへのルーティングを定義する
"""
from flask import Flask, render_template, request, redirect, url_for, session
from subSystems.item import close_itemdb,  Item, Category

# Flaskアプリ初期化
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = " im_secret_key "
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

###以下、エンドポイントへのルーティング
#===================================================================
#テスト用の一覧ページ
#データベースに登録されているデータを全て一覧表示する画面を生成。
#編集ボタン・削除ボタンも合わせて生成して、それをクリックすると各業務に遷移する
@app.route('/')
def test():
    # カテゴリー取得
    categories = Category.get_all()

    # 備品情報クエリ取得
    items = Item.get_all()

    return render_template("test.html", items = items, categories = categories)

#===================================================================
# 備品登録
# @app.route('/add_item', methods=['POST'])
# def add_item():
#     name = request.form["name"]
#     registrant_id = request.form["registrant_id"]
#     remark = request.form.get("remark", "")
#     category_ids = request.form.getlist("category_ids")
#     category_ids = [int(cid) for cid in category_ids]
 
#     Item.insert(name, registrant_id, remark, category_ids)
#     return redirect("/")

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():

    if request.method == 'GET':
        categories = Category.get_all()
        return render_template("registration.html", categories=categories)
    
    elif request.method == 'POST':
        name = request.form["name"].strip()
        registrant_id = request.form["registrant_id"]
        remark = request.form.get("remark", "").strip()#.strip()で空白文字列を削除

        errors = Item.check(name, remark)
        if errors :
            categories = Category.get_all()
            return render_template("registration.html", categories=categories,error=errors)
        
        category_ids = request.form.getlist("category_ids")
        category_ids = [int(cid) for cid in category_ids]
        item_id = Item.insert(name, registrant_id, remark, category_ids)
        result_item = Item.refer(item_id)
        print(result_item)
        return render_template('registration.html',result = result_item)


#===================================================================
# 備品編集
@app.route('/edit_item', methods=['GET','POST'])
def edit_item():
    if request.method == 'GET':
        edit_id = request.args.get("id")
        edit_item = Item.refer(edit_id)
        if not edit_item:
            print("error:route = /edit_item, mesthod=GET")
            return redirect("/")
        categories = Category.get_all()
        return render_template("p006_1.html", item=edit_item, categories=categories, errors=[])

    elif request.method == 'POST':
        id = request.form["id"]
        name = request.form["name"]
        category_ids = [int(cid) for cid in request.form.getlist("category_ids")]
        remark = request.form.get("remark","")

        errors = Item.check(name, remark)
        if errors : #入力形式に問題があったとき、エラーメッセージとともに編集画面をもう一度提示する。
            edit_item = Item.refer(id)
            categories = Category.get_all()
            return render_template("p006_1.html", item=edit_item, categories=categories, errors=errors)
        else:
            edited_item = Item.edit(id, name, category_ids, remark)
            return render_template("p006_2.html", item=edited_item)

#===================================================================
# 備品削除
@app.route('/delete_item', methods=['GET','POST'])
def delete_item():
    if request.method == 'GET':
        delete_id = request.args.get("id")
        delete_item = Item.refer(delete_id)
        if not delete_item:
            print("error:route = /delete_item, mesthod=GET")
            return redirect("/")
        return render_template("p007_1.html", item=delete_item)

    elif request.method == 'POST':
        id = request.form["id"]
        delete_item = Item.delete(id)
        if not delete_item:
            print("error:route = /delete_item, mesthod=POST")
            return redirect("/")
        else:
            return render_template("p007_2.html", item=delete_item)

#===================================================================

### ===== アプリ実行 ===== ###
if __name__ == "__main__":
    # with app.app_context():
        # init_itemdb() 

    app.run(debug=True, host="0.0.0.0", port=5000)