"""
app.py

共通受付システムを想定
エンドポイントへのルーティングを定義する
"""
from flask import Flask, render_template, request, redirect, session, make_response
import io
import pandas as pd
from subSystems.item import close_itemdb, Item, Category
from subSystems.user import close_userdb, User
import os
from werkzeug.utils import secure_filename


# Flaskアプリ初期化
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = " im_secret_key "
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

app.teardown_appcontext(close_itemdb)
app.teardown_appcontext(close_userdb)

# CSVファイルアップロード設定
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """csvのみを受け付ける"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
@app.route('/export')
def export_items():
    items = Item.get_all()

    # DataFrameに変換
    df = pd.DataFrame([
        {
            "id": i["id"],
            "name": i["name"],
            "remark": i["remark"],
            "registrant_id": i["registrant_id"],
            "created_at": i["created_at"],
            "category_ids": ",".join([str(c['id']) for c in i['categories']])
        }
        for i in items
    ])

    # CSV出力
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="cp932")


    # レスポンスとして返す
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=items.csv"
    response.headers["Content-type"] = "text/csv"
    return response
#===================================================================
# TODO: ログアウト処理======================================================================================

@app.route('/logout', methods=['GET', 'POST'])
def logout():

    try:
        # GETリクエスト時（ログアウト確認画面の表示）
        if request.method == 'GET':
            return render_template("P002-1_logout_confirm.html")
        # POSTリクエスト時（ログアウト実行）       
        session.clear()
        return render_template("P002-3_logout_complete.html")
    # 例外処理
    except Exception as e:
        return render_template("P002-2_logout_error.html", error_message=str(e)), 500

#===================================================================
# TODO:利用者削除
@app.route('/delete_userdata', methods=['GET', 'POST'])
def delete_userdata():
    
    # GETアクセス時 -> ユーザー削除入力画面を表示
    if request.method == 'GET':
        return render_template("P004-1_delete_userdata.html")

    # POSTアクセス時 -> フォームのactionとstudentIDを受け取る
    action = request.form.get("action")
    studentID = request.form.get("studentID")
    user = User.get_by_studentID(studentID)
    
    # 削除確認処理    
    if action == "confirm":
        # 入力されたユーザーが存在しない場合
        if not user:
            return render_template("P004-2_delete_userdata_input_error.html", studentID=studentID)
        # すでに削除済み（deadoralive=0）の場合
        elif user["deadoralive"] == 0:
            return render_template("P004-6_delete_userdata_error.html", studentID=studentID)
        # 削除確認画面を表示
        return render_template("P004-3_delete_userdata_confirm.html", user=user)
    
    # 削除処理
    if action == "delete":
        if not user:
            return render_template("P004-4_delete_userdata_error.html", studentID=studentID)
        try:
            result = User.deactivate(studentID)
            if result == 0:# 既に削除済み or 更新なし
                return render_template("P004-6_delete_userdata_error.html", studentID=studentID)
            else:# 今回削除に成功
                return render_template("P004-5_delete_userdata_complete.html", username=user["studentID"])
        except Exception as e:
            # ここはシステムエラー
            return render_template("P004-7_delete_userdata_system_error.html",studentID=studentID, error_message=str(e)), 500

    # キャンセル処理
    if action == "cancel":
        return render_template("P004-1_delete_userdata.html", studentID=studentID)

    # 想定外のaction
    return render_template("P004-2_delete_userdata_input_error.html", studentID=studentID)



#===================================================================
# TODO:インポート
@app.route('/import_items', methods=['GET', 'POST'])
def import_items():
    # GETリクエスト時：アップロード画面を表示
    if request.method == 'GET':
        return render_template("P010-1_import_file_input.html")

    # POSTリクエスト時：アップロードされたファイルを受け取る
    # 複数ファイル対応のため request.files.getlist("file") を使用 
    files = request.files.getlist("file")
    if not files:
        # ファイルが1つも選択されていない場合 → エラー画面へ
        return render_template("P010-2_import_file_format_error.html")

    success_files, failed_files, imported_data = [], [], []

    # 既存の備品データを一旦すべて削除
    Item.clear_all()

    # 受け取ったファイルを1つずつ処理
    for file in files:
        filename = secure_filename(file.filename)  # 安全なファイル名に変換

        # ファイル名が無効 or 拡張子が許可されていない場合
        if not filename or not allowed_file(filename):
            failed_files.append(filename or "不明なファイル")
            continue

        # 一時保存先にファイルを保存
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        ok, items = Item.import_from_file(filepath)
        if ok:# インポート成功
            success_files.append(filename)
            imported_data.extend(items)   # 成功したファイルのアイテム詳細を追加
        else:# インポート失敗
            failed_files.append(filename)
    # 完了画面に成功・失敗の結果を渡す
    return render_template(
        "P010-5_import_complete.html",
        success_files=success_files,
        failed_files=failed_files,
        imported_data=imported_data
    )




### ===== アプリ実行 ===== ###
if __name__ == "__main__":
    # with app.app_context():
    #     init_itemdb() 

    app.run(debug=True, host="0.0.0.0", port=5000)