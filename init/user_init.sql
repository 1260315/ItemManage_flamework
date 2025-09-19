/*
user_seed.sql

利用者データベースの初期化
*/

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS user_db;

USE user_db;

DROP TABLE IF EXISTS users;

/*--テーブルの作成-----------------------------------------*/
CREATE TABLE IF NOT EXISTS users (
    studentID VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    authority TINYINT(1) NOT NULL DEFAULT -1 , -- 0=管理者 / 1=一般ユーザ
    deadoralive TINYINT(1) NOT NULL DEFAULT 1 -- 0=死亡 / 1=生存
);

/*--初期データの投入----------------------------------------*/
INSERT INTO users (studentID, password_hash, authority) VALUES
('1260315', 'scrypt:32768:8:1$gKCKLZGULRZ2HhQq$a957abee3f41180ec01a90dd46b51b6ef6d2d8352abd4fe92d5edd5f4ce2f3ae17b749321025be92562951ccb774cb019bb9860f0725de7507bd6d2ab23a2606', 0), -- 管理者
('1260999', 'password999', 1), -- 一般ユーザ
('1260888', 'password888', 1); -- 一般ユーザ