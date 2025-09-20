"""
app.py

共通受付システムを想定
エンドポイントへのルーティングを定義する
"""
from flask import Flask, render_template, request, redirect, url_for, session, abort, send_file
from subSystems.item import close_itemdb, Item, Category
from subSystems.user import close_userdb, User
import os
import pandas as pd
from werkzeug.utils import secure_filename
from pandas.errors import EmptyDataError

# Flaskアプリ初期化
app = Flask(__name__)
app.secret_key = " im_secret_key "
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

app.teardown_appcontext(close_itemdb)
app.teardown_appcontext(close_userdb)

###以下、エンドポイントへのルーティング
#===================================================================
#業務一覧画面
@app.route('/', methods=['GET','POST'])
def home():

    if request.method == 'GET':

        authority = User.logincheck(session)
        if authority == -1:
            return redirect("/login")
        elif authority == 0:
            return render_template('p001_2.html')
        elif authority == 1:
            return render_template('p001_3.html')

#===================================================================
#利用者登録
@app.route('/add_user', methods=['GET','POST'])
def register_user():

    authority = User.logincheck(session)
    if authority == -1:
        return redirect("/login")
    elif authority == 1:
        return redirect("/forbidden")
    
    if request.method == 'GET':
        return render_template("p003_1.html", errors=[])
    else:
        studentID = request.form['studentID']
        password = request.form['password']
        authority = request.form.get('authority')

        #入力値チェック
        errors = User.check(studentID, password, authority)
        if errors:
            return render_template("p003_1.html", errors=errors,studentID=studentID,password=password,authority=authority)
        
        #既に登録された学籍番号でないかチェック
        if User.exists(studentID):

            #再登録
            add_user = User.get_by_studentID(studentID)
            deadoralive = add_user["deadoralive"]
            if deadoralive == 0:
                #「削除済みのユーザーです。再登録しますか？」
                return render_template("p003_4.html",studentID=studentID,password=password,authority=authority)

            else:

                errors=[f"学籍番号 {studentID} は既に登録されています"]
                return render_template("p003_2.html",errors=errors)
        
        #登録
        User.insert(studentID, password, authority)
        return render_template("p003_3.html",studentID=studentID)     
    
#===================================================================
#利用者再登録
@app.route('/re_add_user', methods=['GET','POST'])
def re_add_user():
    
    if request.method == "GET":
        return render_template("p003_1.html")
    
    elif request.method == "POST":
        studentID = request.form['studentID']
        password = request.form['password']
        authority = request.form.get('authority')

        User.delele(studentID)

        #登録
        User.insert(studentID, password, authority)
        return render_template("P003_3.html",studentID=studentID)     
    

#===================================================================
# 利用者削除
@app.route("/delete_user", methods=["GET", "POST"])
def delete_user():
        
    authority = User.logincheck(session)
    if authority == -1:
        return redirect("/login")
    elif authority != 0:
        return redirect("/forbidden")
    
    if request.method == "GET":
        return render_template("p004_1.html")
    
    if request.method == "POST":

        action = request.form.get("action")
        studentID = request.form.get("studentID")
        user = User.get_by_studentID(studentID)
        # 削除確認処理    
        if action == "confirm":
            # 入力されたユーザーが存在しない場合
            if not user:
                return render_template("p004_2.html", studentID=studentID)
            # すでに削除済み（deadoralive=0）の場合
            elif user["deadoralive"] == 0:
                return render_template("p004_6.html", studentID=studentID)
            # 削除確認画面を表示
            return render_template("p004_3.html", user=user)
        
        # 削除処理
        if action == "delete":
            if not user:
                return render_template("p004_4.html", studentID=studentID)
            try:
                result = User.deactivate(studentID)
                if result == 0:# 既に削除済み or 更新なし
                    return render_template("p004_6.html", studentID=studentID)
                else:# 今回削除に成功
                    return render_template("p004_5.html", username=user["studentID"])
            except Exception as e:
                # ここはシステムエラー
                return render_template("p004_7.html",studentID=studentID, error_message=str(e)), 500

        # キャンセル処理
        if action == "cancel":
            return render_template("p004_1.html", studentID=studentID)

        # 想定外のaction
        return render_template("p004_2.html", studentID=studentID)

    
#===================================================================
#ログイン
@app.route('/login', methods=['GET','POST'])
def login():
    # authority = User.logincheck(session)
    # if authority != -1:
    #     return redirect("/forbidden")
    
    if request.method == 'GET':
        return render_template("p001_1.html", error=None)
    else:
        studentID = request.form['studentID']
        password = request.form['password']
        user = User.authenticate(studentID, password)

        #入力値チェック
        errors = User.check(studentID, password, -1)
        if errors:
            return render_template("p001_1.html", errors=errors,studentID=studentID,password=password)

        if user:
            session['studentID'] = user.studentID
            session['authority'] = user.authority
            
            return redirect("/")
        
        else:
            return render_template("p001_4.html", error="学籍番号またはパスワードが違います")

#===================================================================
#ログアウト
@app.route('/logout', methods=['GET','POST'])
def logout():
    authority = User.logincheck(session)
    if authority == -1:
        return redirect("/login")
    session.clear()
    return redirect('/login')

#===================================================================
# 備品登録
@app.route('/add_item/', methods=['GET', 'POST'])
def add_item():
    
    authority = User.logincheck(session)
    if authority == -1:
        return redirect("/login")
    else:
    
        if request.method == 'GET':
            categories = Category.get_all()
            return render_template("registration.html", errors=[], categories=categories)
        
        elif request.method == 'POST':
            categories = Category.get_all()
            name = request.form["name"].strip()
            registrant_id = session["studentID"]
            remark = request.form.get("remark", "").strip()     #.strip()で空白文字列を削除

            errors = Item.check(name, remark)
            if errors :
                categories = Category.get_all()
                return render_template("registration.html", categories=categories, errors=errors)

            category_ids = request.form.getlist("category_ids")
            category_ids = [int(cid) for cid in category_ids]
            item_id = Item.insert(name, registrant_id, remark, category_ids)
            result_item = Item.refer(item_id)
            return render_template('registration.html', categories=categories, errors = [], result = result_item)

#===================================================================
# 備品編集
@app.route('/edit_item/', methods=['GET','POST'])
def edit_item():

    authority = User.logincheck(session)
    if authority == -1:
        return redirect("/login")
    else:

        if request.method == 'GET':
                edit_id = request.args.get("id")
                edit_item = Item.refer(edit_id)

                if not edit_item:
                    print("error:route = /edit_item, mesthod=GET")
                    return redirect("/")

                if authority == 1 and int(session["studentID"]) != edit_item["registrant_id"]:
                    print("不正なアクセス！登録者IDとセッションIDが一致していません")
                    print(session['studentID'])
                    print(edit_item["registrant_id"])
                    return redirect("/forbidden")
                
                categories = Category.get_all()
                return render_template("p006_1.html", item=edit_item, categories=categories, errors=[])

        elif request.method == 'POST':

            id = request.form["id"]
            name = request.form["name"]
            category_ids = [int(cid) for cid in request.form.getlist("category_ids")]
            remark = request.form.get("remark","")

            edit_item = Item.refer(id)
            if not edit_item:
                    print("error:route = /edit_item, mesthod=GET")
                    return redirect("/")

            if authority == 1 and int(session["studentID"]) != edit_item["registrant_id"]:
                print("不正なアクセス！登録者IDとセッションIDが一致していません")
                return redirect("/forbidden")

            errors = Item.check(name, remark)
            if errors : #入力形式に問題があったとき、エラーメッセージとともに編集画面をもう一度提示する。
                categories = Category.get_all()
                return render_template("p006_1.html", item=edit_item, categories=categories, errors=errors)
            else:
                edited_item = Item.edit(id, name, category_ids, remark)
                return render_template("p006_2.html", item=edited_item)

#===================================================================
# 備品削除
@app.route('/delete_item/', methods=['GET','POST'])
def delete_item():

    authority = User.logincheck(session)
    if authority == -1:
        return redirect("/login")
    else:

        if request.method == 'GET':
            delete_id = request.args.get("id")
            delete_item = Item.refer(delete_id)
            if not delete_item:
                print("error:route = /delete_item, mesthod=GET")
                return redirect("/")
            
            if authority == 1 and int(session["studentID"]) != delete_item["registrant_id"]:
                print("不正なアクセス！登録者IDとセッションIDが一致していません")
                return redirect("/forbidden")

            return render_template("p007_1.html", item=delete_item)

        elif request.method == 'POST':
            delete_id = request.form["id"]
            delete_item = Item.refer(delete_id)

            if authority == 1 and int(session["studentID"]) != delete_item["registrant_id"]:
                print("不正なアクセス！登録者IDとセッションIDが一致していません")
                return redirect("/forbidden")

            delete_item = Item.delete(delete_id)
            if not delete_item:
                print("error:route = /delete_item, mesthod=POST")
                return redirect("/")
            else:
                return render_template("p007_2.html", item=delete_item)


#===================================================================
#エラー

#不正なアクセスのとき
@app.route("/forbidden")
def forbidden():
    abort(403)
#===================================================================
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
    if 'sortOrder' not in session:
        session['sortOrder'] = "id"
    if 'sortDirection' not in session:
        session['sortDirection'] = True
    
    order = request.args.get("sort")
    do_sort = request.args.get("do_sort","")
    if order and do_sort == "1":       
        Item.sort(order,session)
    values = []
    for key, type in FIELDS:
        if type == "str":    
            values.append((key, request.args.get(key,"")))
        elif type == "list":
            values.append((key, request.args.getlist(f"{key}[]")))

    rows = Item.search(values,session)
    categories = Category.get_all()
    return render_template('p008.html',rows=rows, categories=categories)

#===================================================================
#備品情報エクスポート
@app.route('/export_items', methods=['GET','POST'])
def export_items():

    authority = User.logincheck(session)
    if authority == -1:
        return redirect("/login")
    
    if request.method == 'GET':
        
        return render_template("p009_1.html", error=None)
    
    if request.method == 'POST':

        output = Item.export_csv()

        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='items.csv'
        )

#===================================================================
# CSVファイルアップロード設定
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """csvのみを受け付ける"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#===================================================================
# インポート
@app.route('/import_items', methods=['GET', 'POST'])
def import_items():
    if request.method == 'GET':
        # ファイル入力画面を表示
        return render_template("p010_1.html")

    # POST時に hidden で渡される "step" の値を確認
    # デフォルトは "upload"
    step = request.form.get("step", "upload")

    if step == "upload":
        # アップロードされたファイル群を取得
        files = request.files.getlist("file")
        if not files:
            # ファイル未選択 → エラー画面へ
            return render_template(
                "p010_2.html",
                invalid_files=["ファイルが選択されていません"]
            )

        invalid_files, temp_paths, preview_data = [], [], []

        # 各ファイルを保存
        for file in files:
            filename = secure_filename(file.filename)
            if not filename or not allowed_file(filename):
                invalid_files.append(filename or "不明なファイル")
            else:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                temp_paths.append(filepath)

        if invalid_files:
            # CSV以外が含まれていた場合 → エラー画面へ
            return render_template("p010_2.html", invalid_files=invalid_files)

        preview_data = []

        # 各CSVファイルを読み込み
        for p in temp_paths:
            try:
                # CSV → pandas.DataFrame に変換
                df = pd.read_csv(p, encoding="utf-8")
            except EmptyDataError:
                # ファイルが空だった場合
                return render_template(
                    "p010_4.html",
                    filename=os.path.basename(p),
                    message="CSVファイルが空です"
                )

            # ヘッダーだけでデータ行がない場合
            if df.empty:
                return render_template(
                    "p010_4.html",
                    filename=os.path.basename(p),
                    message="CSVファイルにデータがありません"
                )

            # DataFrame を dict に変換し、プレビュー用データを準備
            rows = df.to_dict(orient="records")
            preview_data.append({
                "filename": os.path.basename(p),
                "rows": rows
            })

        # 確認画面
        return render_template(
            "p010_3.html",
            temp_paths=temp_paths,   # hiddenで渡してcommit時に再利用
            preview_data=preview_data
        )

    elif step == "commit":
        temp_paths = request.form.getlist("temp_paths")
        success_files, failed_files, imported_data = [], [], []

        # 既存データをクリアしてから再インポート
        Item.clear_all()

        for filepath in temp_paths:
            filename = os.path.basename(filepath)

            if not os.path.exists(filepath):
                failed_files.append({"filename": filename, "reason": "ファイルが存在しません"})
                continue

            ok, result = Item.import_from_file(filepath)
            if ok:
                success_files.append(filename)
                imported_data.extend(result)
            else:
                failed_files.append({"filename": filename, "reason": result})

            # os.remove(filepath)  # 読み込み後に削除


        # 成功・失敗どちらも表示
        return render_template("p010_4.html",
            success_files=success_files,
            failed_files=failed_files,
            imported_data=imported_data)

### ===== アプリ実行 ===== ###
if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=5000)