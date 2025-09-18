"""
app.py

共通受付システムを想定
エンドポイントへのルーティングを定義する
"""
from flask import Flask, render_template, request, redirect, url_for, session
from subSystems.item import close_itemdb, Item, Category
from subSystems.user import close_userdb, User

# Flaskアプリ初期化
app = Flask(__name__)
app.secret_key = " im_secret_key "
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

app.teardown_appcontext(close_itemdb)
app.teardown_appcontext(close_userdb)

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
#業務一覧画面
@app.route('/home', methods=['GET','POST'])
def home():

    authority = session['authority']
    if authority == 0:
         return render_template('p001_2.html')
    else:
         return render_template('p001_3.html')

#===================================================================
#利用者登録
@app.route('/register_user', methods=['GET','POST'])
def register_user():
    if request.method == 'GET':
        return render_template("p003_1.html", errors=[])
    else:
        studentID = request.form['studentID']
        password = request.form['password']
        #authority = request.form.get('authority', 1)  #権限は絶対入力
        authority = request.form['authority']

        #入力値チェック
        errors = User.check(studentID, password)
        if errors:
            return render_template("P003_2.html", errors=errors)
        
        #既に登録された学籍番号でないかチェック
        """
        existing_user = User.query.filter_by(studentID=studentID).first()
        if existing_user:
            errors = [f"学籍番号 {studentID} は既に登録されています"]
            return render_template("P003-2_userregistererror.html", errors=errors)
        """
        #登録
        User.insert(studentID, password, authority)
        return render_template("P003_3.html",studentID=studentID)     
    
#===================================================================
#ログイン
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("p001_1.html", error=None)
    else:
        studentID = request.form['studentID']
        password = request.form['password']
        user = User.authenticate(studentID, password)


        if user:
            session['studentID'] = user.studentID
            session['authority'] = user.authority
            
           
               
            return redirect("/home")
           
        else:
            return render_template("p001_4.html", error="学籍番号またはパスワードが違います")

#===================================================================
# 備品登録
@app.route('/add_item/', methods=['GET', 'POST'])
def add_item():

    if request.method == 'GET':
        categories = Category.get_all()
        return render_template("registration.html", categories=categories)
    
    elif request.method == 'POST':
        name = request.form["name"].strip()
        registrant_id = request.form["registrant_id"]
        remark = request.form.get("remark", "").strip()#.strip()で空白文字列を削除
        if not name or not remark:#未入力チェック
            return "備品名と登録者IDは必須入力項目です",400
        
        category_ids = request.form.getlist("category_ids")
        category_ids = [int(cid) for cid in category_ids]
        Item.insert(name, registrant_id, remark, category_ids)
        return redirect("/")

#===================================================================
# 備品編集
@app.route('/edit_item/', methods=['GET','POST'])
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
@app.route('/delete_item/', methods=['GET','POST'])
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

    app.run(debug=True, host="0.0.0.0", port=5000)