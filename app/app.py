"""
app.py

共通受付システムを想定
エンドポイントへのルーティングを定義する
"""
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import io
import pandas as pd
from subSystems.item import close_itemdb, Item, Category
from subSystems.user import close_userdb, User
from flask_wtf import CSRFProtect
import hashlib

app = Flask(__name__)
# Flaskアプリ初期化
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = "e515d0d63d0f6821ddec6bf61af081e91dacf627b4e852496d54bfba5755af5c"
#csrf = CSRFProtect(app)
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
        delete_id = request.args.get("del")
        delete_item = Item.refer(delete_id)
        if not delete_item:
            print("error:route = /delete_item, mesthod=GET")
            return redirect("/")
        return render_template("p007_1.html", item=delete_item)

    elif request.method == 'POST':
        id = request.form["del"]
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

    
    if 'studentID' in session and 'authority'in session:
        authority = session['authority']
        print(session['studentID'])
        print(session['authority']) 
        if authority == 0:
            return render_template('P001-2_home.html')
        elif authority == 1:
            return render_template('P001-3_home.html')
    return redirect('/login')

#===================================================================
#利用者登録
@app.route('/register_user', methods=['GET','POST'])
def register_user():
    if request.method == 'GET':
        return render_template("P003-1_userregister.html", errors=[])
    else:
        studentID = request.form['studentID']
        password = request.form['password']
        #authority = request.form.get('authority', 1)  #権限は絶対入力
        authority = request.form['authority']

        #入力値チェック
        errors = User.check(studentID, password)
        if errors:
            return render_template("P003-2_userregistererror.html", errors=errors)
        
        #既に登録された学籍番号でないかチェック
        """
        existing_user = User.query.filter_by(studentID=studentID).first()
        if existing_user:
            errors = [f"学籍番号 {studentID} は既に登録されています"]
            return render_template("P003-2_userregistererror.html", errors=errors)
        """
        #登録
        User.insert(studentID, password, authority)
        return render_template("P003-3_userregistercomplate.html",studentID=studentID)     
    
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
@app.route('/export_items')
def export_items():
    #ログインしているかの判定
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    items = Item.get_all()#Itemクラスを使ってすべての備品情報を取得

    # 3. DataFrame に変換
    df = pd.DataFrame([{
        '備品ID': i['item_id'],
        '備品名': i['name'],
        'カテゴリ':i['category_id'],
        '登録者': i['registrant_id'],
        '登録日':i[''],
        '備考': i['remark']
    } for i in items])
    
    output = io.StringIO()#空のメモリ上の文字列バッファを作成
    df.to.csv(output,index=False,enconding='utf8')
    output.seek(0)
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='items.csv'
    )  
#===================================================================
#===================================================================
# エクスポート（CSV）
@app.route('/logout', methods=['GET','POST'])
def logout():
    session.clear()
    return redirect('/login')

#備品検索
@app.route('/items', methods=['GET', 'POST'])
def search():
    if 'studentID' not in session:
        return redirect('/login')
    FIELDS = [("name","str"),
          ("id","str"),
          ("created_at","str"),
          ("registrant_id","str"),
          ("category_id","list")]
    #session['authority'] = User.getAuthority(session['studentID'])
    print(session['studentID'])
    print(session['authority'])
    if 'sortOrder' not in session:
        session['sortOrder'] = "id"
    if 'sortDirection' not in session:
        session['sortDirection'] = True
    commands = []
    params = []
    sql = """select items.id, items.name, items.created_at, items.registrant_id,
            categories.name as category_id, items.remark 
            from items join categories on items.category_id = categories.id """
    
    order = request.args.get("sort")
    if order:       
        session['sortOrder'], session['sortDirection'] = Item.sort(order,session)
    values = []
    for key, type in FIELDS:
        if type == "str":    
            values.append((key, request.args.get(key,"")))
        elif type == "list":
            #print('ok')
            values.append((key, request.args.getlist(f"{key}[]")))

    rows = Item.search(values,session)
    #print(rows)
    return render_template('P008.html',rows=rows)
    

### ===== アプリ実行 ===== ###
if __name__ == "__main__":
    # with app.app_context():
    #     init_itemdb() 

    app.run(debug=True, host="0.0.0.0", port=5000)