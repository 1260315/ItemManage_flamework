/*
user_seed.sql

利用者データベースの初期化
*/
CREATE DATABASE IF NOT EXISTS user_db;

USE user_db;

DROP TABLE IF EXISTS users;

/*--テーブルの作成-----------------------------------------*/
CREATE TABLE IF NOT EXISTS users (
    studentID VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    authority TINYINT(1) NOT NULL DEFAULT 1 , -- 0=管理者 / 1=一般ユーザ
    deadoralive TINYINT(1) NOT NULL DEFAULT 1 -- 0=死亡 / 1=生存
);

/*--初期データの投入----------------------------------------*/
INSERT INTO users (studentID, password_hash, authority) VALUES
('1260315', 'password123', 0), -- 管理者
('1260999', 'password999', 1), -- 一般ユーザ
('1260888', 'password888', 1); -- 一般ユーザ
