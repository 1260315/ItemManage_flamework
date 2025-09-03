# Dockerとは
Dockerとは、コンテナ型の仮想環境を作成・配布・実行するためのもの。
コンテナ型とは、ホストOS※1を動かしているカーネルを利用して、あたかもゲストOS※2があるように仮想環境を作り上げる。（※1 計算器自体のOS　※2仮想環境で利用するOS）
<img width="717" height="472" alt="466407611-d9429c11-2740-4d3a-b1c7-06b997fcc40c" src="https://github.com/user-attachments/assets/c6fb9243-235b-4e2e-ac34-17bd9515669d" />
<br>

今回は、PythonやHTMLのコーディングは、ホストOSで行う。Docker Composeのイメージをビルド、ビルドしてできたコンテナを起動することで、appディレクトリの中身をコピー・Mysqlの起動・app.pyの実行をすべて自動でさせることができる。
Docker Composeの説明は省略。

# リポジトリの使い方

## リポジトリのデータを取り込むには？

### 0.Windowsでのgitの準備
Windowsではgitをインストールする必要がある。
以下のWebサイトの①、②を実施する。<br>
https://prog-8.com/docs/git-env-win  <br>

### 1.クローンする
レポジトリをクローンしたいディレクトリに移動して、以下のコマンドを実行する。

```
git clone https://github.com/1260315/ItemManage_flamework.git
```
ディレクトリをlsで見ると、ItemManage_flameworkというディレクトリが追加されているはず。

### 2.プルする
新しく更新された内容を反映したいときは、クローンしたリポジトリでpullできるはず。たぶん。
```
git pull --rebase
```

## Dockerの使い方
コンテナを起動すると、mysqlとapp.pyが立ち上がって、Webページ (http://localhost:5000/) が開けるようになる。

### 1.Dockerをインストールする
以下のWebページを参考に、Docker Desktopをインストールする。
https://qiita.com/zembutsu/items/a98f6f25ef47c04893b3

### 2.ビルド・起動
クローンしたItem-management-systemディレクトリで、コンテナをビルド・起動する。
```
docker-compose -f ./docker-compose.yml up --build
```

