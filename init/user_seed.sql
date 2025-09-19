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
    authority TINYINT(1) NOT NULL DEFAULT 1 , -- 0=管理者 / 1=一般ユーザ
    deadoralive TINYINT(1) NOT NULL DEFAULT 1 -- 0=死亡 / 1=生存
);

/*--初期データの投入----------------------------------------*/
INSERT INTO users (studentID, password_hash, authority) VALUES
('1260315', 'scrypt:32768:8:1$MFOatH0CM1v2hKfT$48482904d26ad0c980efb5fd206ba839c30255a060e61366e027f2792123254c90a2d90f117c9c9f9fa789234bd83a011fea5c6f1d578237ab76ffbeb11a8811', 0), -- 管理者
('1260999', 'scrypt:32768:8:1$IqXa8mDSEbV0XEcG$e24ccb1a74c962647e11b68752ab8d7bfa00b3df65b9bf9393c4d0a839383ec66c0ca4c725fc4427e42cc7eb92469aad753d1e504405246f690754918aa3545a', 1), -- 一般ユーザ
('1260888', 'password888', 1); -- 一般ユーザ


