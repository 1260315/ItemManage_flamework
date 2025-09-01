"""
config.py

Flaskアプリの設定を定義するファイル。
複数のデータベースに接続する。
"""

# 会員管理データベースURI
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@db/auth_db'

# 備品情報データベースURI
# URI : Uniform Resource Identifier（統一リソース識別子）
EQUIPMENT_DB_URI = 'mysql+pymysql://root:password@db/equipment_db'

# DBバインド設定
SQLALCHEMY_BINDS = {
    'auth': SQLALCHEMY_DATABASE_URI,
    'item': EQUIPMENT_DB_URI,
}

# SQLAlchemyの追跡機能を無効化（パフォーマンス改善）
SQLALCHEMY_TRACK_MODIFICATIONS = False