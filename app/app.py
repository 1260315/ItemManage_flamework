"""
app.py

共通受付システムを想定
エンドポイントへのルーティングを定義する
"""
from flask import Flask, render_template, request, redirect, url_for, session,send_file
import io
import datetime
import pandas as pd
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
# 備品登録
@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form["name"]
    registrant_id = request.form["registrant_id"]
    remark = request.form.get("remark", "")
    category_ids = request.form.getlist("category_ids")
    category_ids = [int(cid) for cid in category_ids]
 
    Item.insert(name, registrant_id, remark, category_ids)
    return redirect("/")

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
#
@app.route('/home', methods=['GET','POST'])
def home():

    authority = session['authority']
    if authority == 0:
         return render_template('P001-2_home.html')
    else:
         return render_template('P001-3_home.html')

#===================================================================
#利用者登録
@app.route('/register_user', methods=['GET','POST'])
def register_user():
    if request.method == 'POST':
        #authority = -1
        studentID = request.form['studentID']
        password = request.form['password']
        authority = request.form.get('authority')



        #入力値チェック
        errors = User.check(studentID, password,authority)
        if errors:
            return render_template("P003-1_userregister.html", errors=errors)
        
        #既に登録された学籍番号でないかチェック
        if User.exists(studentID):

            #再登録
            add_user = User.get_by_studentID(studentID)
            deadoralive = add_user["deadoralive"]
            if deadoralive == 0:
                #「削除済みのユーザーです。再登録しますか？」
                return render_template("P003-4_userleregister.html",studentID=studentID,password=password,authority=authority)

            else:
                errors=[f"学籍番号 {studentID} は既に登録されています"]
                return render_template("P003-2_userregistererror.html",errors=errors)

        #登録
        User.insert(studentID, password, authority)
        return render_template("P003-3_userregistercomplate.html",studentID=studentID)     

    else:
        return render_template('P003-1_userregister.html')

#===================================================================
#利用者再登録
@app.route('/reregister_user', methods=['GET','POST'])
def reregister_user():
    if request.method == 'POST':

        studentID = request.form['studentID']
        password = request.form['password']
        authority = request.form.get('authority')

        User.delele(studentID)

        #登録
        User.insert(studentID, password, authority)
        return render_template("P003-3_userregistercomplate.html",studentID=studentID)     

    else:
        return render_template('P003-1_userregister.html')

   
#===================================================================
#ログイン
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("P001-1_login.html", error=None)
    else:
        studentID = request.form['studentID']
        password = request.form['password']
        user = User.authenticate(studentID, password)


        if user:
            session['studentID'] = user.studentID
            session['authority'] = user.authority    
            return redirect("/home")
        else:
            return render_template("P001-4_roginerror.html", error="学籍番号またはパスワードが違います")

#===================================================================
# エクスポート（CSV）
@app.route('/export_items', methods=['GET','POST'])
def export_items():
    
    return render_template("P009-1_export.html", error=None)

#===================================================================
# エクスポートcheck（CSV）
@app.route('/export_check', methods=['GET','POST'])
def export_check():
    

    items = Item.get_all()#Itemクラスを使ってすべての備品情報を取得
     

    for i in items:
        created_at = i.get('created_at')
        if isinstance(created_at, datetime.datetime):
            i['created_at'] = created_at.strftime("%Y-%m-%d %H:%M:%S")
        elif created_at is None:
            i['created_at'] = ''

        #category_itemから
        i['categories'] = Item.get_category_names(i['id'])

    # 3. DataFrame に変換
    df = pd.DataFrame([{
        '備品ID': i['id'],
        '備品名': i['name'],
        'カテゴリ':i['categories'],
        '登録者': i['registrant_id'],
        '登録日':i['created_at'],
        '備考': i['remark']
     } for i in items])

    
    output = io.BytesIO()#空のメモリ上の文字列バッファを作成
    df.to_csv(output,index=False,encoding='utf-8-sig')
    output.seek(0)

    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='items.csv'
    )  

### ===== アプリ実行 ===== ###
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)