"""
subSystems/user.py

備品情報管理システムを想定。
利用者情報データベースのテーブルを定義する
"""
import mysql.connector
from flask import g
from werkzeug.security import check_password_hash, generate_password_hash



def get_userdb():
    if "user_db" not in g:
        g.user_db = mysql.connector.connect(
            host="db",
            user="root",
            password="password",
            database="user_db",
            autocommit=True
        )

    print("user_dbとのコネクションを確立できました！")

    return g.user_db

def close_userdb(e=None):  # e=None は Flask の teardown でコールバックする際に event引数を受け取るためのデフォルト値
    user_db = g.pop("user_db", None)
    if user_db is not None:
        user_db.close()

# #初期化
# def init_userdb():
#     db = get_userdb()
#     cursor = db.cursor()

#     with open("seed_users.sql", encoding="utf-8") as f:
#         sql_commands = f.read().split(";")

#     for command in sql_commands:
#         command = command.strip()
#         if command:
#             cursor.execute(command)

#     cursor.close()
#     close_userdb()
#     print("ユーザDBを初期化しました")

# =======================================================
# 利用者テーブルの操作
# users テーブル: id(PK), studentID, password_hash, created_at
# =======================================================

class User:
    def __init__(self, studentID, authority):
        self.studentID = studentID
        self.authority = authority

    @classmethod
    def get_all(cls):
        """全ユーザを取得"""
        db = get_userdb()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT studentID, authority FROM users")
        data = cursor.fetchall()
        cursor.close()
        return data

    @classmethod
    def get_by_studentID(cls, studentID):
        """学籍番号指定でユーザ取得"""
        db = get_userdb()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE studentID=%s", (studentID,))
        data = cursor.fetchone()
        cursor.close()
        return data

    @classmethod
    def insert(cls, studentID, password, authority):
        """ユーザ新規登録"""
        db = get_userdb()
        cursor = db.cursor()
        password_hash = generate_password_hash(password)
        cursor.execute(#sqlに入れる
            "INSERT INTO users (studentID, password_hash, authority) VALUES (%s, %s, %s)",
            (studentID, password_hash, authority)
        )
        cursor.close()
        db.commit()

    # @classmethod
    # def update_password(cls, uid, new_password):
    #     """パスワード変更"""
    #     db = get_userdb()
    #     cursor = db.cursor()
    #     password_hash = generate_password_hash(new_password)
    #     cursor.execute(
    #         "UPDATE users SET password_hash=%s WHERE id=%s",
    #         (password_hash, uid)
    #     )
    #     cursor.close()
    #     db.commit()

    # @classmethod
    # def update_authority(cls, uid, authority):
    #     """権限変更"""
    #     db = get_userdb()
    #     cursor = db.cursor()
    #     cursor.execute("UPDATE users SET authority=%s WHERE id=%s", (authority, uid))
    #     cursor.close()
    #     db.commit()

    # @classmethod
    # def delete(cls, uid):
    #     """ユーザ削除"""
    #     db = get_userdb()
    #     cursor = db.cursor()
    #     cursor.execute("DELETE FROM users WHERE id=%s", (uid,))
    #     cursor.close()
    #     db.commit()

    @classmethod
    def authenticate(cls, studentID, password):
        """学籍番号とパスワードでユーザーを認証:ログイン"""
        
        print( generate_password_hash("password123"))

        db = get_userdb()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE studentID = %s", (studentID,))
        
        row = cursor.fetchone()
        print(row)
        cursor.close()

        if row and check_password_hash(row["password_hash"], password):
            # 認証成功

            return cls(studentID=row["studentID"], authority=row["authority"])
        else:
            # 認証失敗
            return None

    @staticmethod
    def exists(studentID):
        db = get_userdb()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE studentID = %s", (studentID,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None

    @classmethod
    def check(cls, studentID, password,authority):
        """入力チェック"""
        errors = {}
        if not studentID:
            errors["studentID"] = "学籍番号は必須です。"
        elif len(studentID) > 20:
            errors["studentID"] = "学籍番号は20文字以内で入力してください。"
        if not password:
            errors["password"] = "パスワードは必須です。"
        elif len(password) < 6:
            errors["password"] = "パスワードは6文字以上で入力してください。"
        if  authority is None:
            print("ああああああああああああ")
            errors["authority"] = "権限の選択は必須です。"
        return errors
