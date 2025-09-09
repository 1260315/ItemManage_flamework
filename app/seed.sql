/*
seed.sql

データベースの初期化
*/

--#item_db================================================

--DBの作成
DROP DATABASE IF EXISTS item_db;
CREATE DATABASE IF NOT EXISTS item_db;

USE item_db;

--テーブルの作成-------------------------------------------

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(10) NOT NULL,
    registrant_id INT NOT NULL,
    remark VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS item_category (
    item_id INT,
    category_id INT,
    PRIMARY KEY (item_id, category_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

--初期データの投入--------------------------------------------
INSERT INTO categories (name) VALUES
("PC"), ("モニター"), ("マウス"), ("キーボード"), ("プリンター"), ("その他");

INSERT INTO items (name, registrant_id, remark) VALUES
("パソコン一式", 1260315, "ケーブルもあるよ!");

INSERT INTO item_category (item_id, category_id) VALUES
(1,1),(1,2),(1,3),(1,4),(1,5);
