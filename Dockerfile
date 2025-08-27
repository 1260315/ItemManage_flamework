# ベースイメージとして公式のPythonイメージを使用
FROM python:3.12

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ローカルのrequirements.txtをコンテナにコピー
COPY requirements.txt .
# config周りをコンテナにコピー(start.sh、gunicorn_config.py)
# これは本番環境用なので、開発時には使わない

# Pythonの依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコンテナにコピー
COPY /app/ .
RUN chmod 755 ./gunicorn_setting/start.sh

# CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]