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

    return g.user_db

def close_userdb(e=None):  # e=None は Flask の teardown でコールバックする際に event引数を受け取るためのデフォルト値
    user_db = g.pop("user_db", None)
    if user_db is not None:
        user_db.close()

#初期化
def init_userdb():
    db = get_userdb()
    cursor = db.cursor()

    with open("seed_users.sql", encoding="utf-8") as f:
        sql_commands = f.read().split(";")

    for command in sql_commands:
        command = command.strip()
        if command:
            cursor.execute(command)

    cursor.close()
    close_userdb()
    print("ユーザDBを初期化しました")

# =======================================================
# 利用者テーブルの操作
# users テーブル: id(PK), studentID, password_hash, created_at
# =======================================================

class User:

    @classmethod
    def get_all(cls):
        """全ユーザを取得"""
        db = get_userdb()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, studentID, role FROM users")
        data = cursor.fetchall()
        cursor.close()
        return data

    @classmethod
    def get_by_id(cls, uid):
        """ID指定でユーザ取得"""
        db = get_userdb()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, studentID, role FROM users WHERE id=%s", (uid,))
        data = cursor.fetchone()
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
    def insert(cls, studentID, password, authority=1):
        """ユーザ新規登録"""
        db = get_userdb()
        cursor = db.cursor()
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (studentID, password_hash, authority) VALUES (%s, %s, %s)",
            (studentID, password_hash, authority)
        )
        cursor.close()
        db.commit()

    @classmethod
    def update_password(cls, uid, new_password):
        """パスワード変更"""
        db = get_userdb()
        cursor = db.cursor()
        password_hash = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE id=%s",
            (password_hash, uid)
        )
        cursor.close()
        db.commit()

    @classmethod
    def update_authority(cls, uid, authority):
        """権限変更"""
        db = get_userdb()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET authority=%s WHERE id=%s", (role, uid))
        cursor.close()
        db.commit()

    @classmethod
    def delete(cls, uid):
        """ユーザ削除"""
        db = get_userdb()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (uid,))
        cursor.close()
        db.commit()

    @classmethod
    def verify_password(cls, studentID, password):
        """ログイン用認証"""
        user = cls.get_by_studentID(studentID)
        if user and check_password_hash(user["password_hash"], password):
            return user  # user["authority"]で0か1か確認できる
        return None
    
    @classmethod
    def authenticate(cls, studentID, password):
        """学籍番号とパスワードでユーザを認証して返す。失敗ならNone"""
        user = cls.verify_password(studentID=studentID).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @classmethod
    def check(cls, studentID, password):
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
        return errors
