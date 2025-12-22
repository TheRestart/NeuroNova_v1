-- CDSS 데이터베이스 설정 스크립트
-- MySQL 8.0+ 권장

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS cdss_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 사용자 생성 및 권한 부여
CREATE USER IF NOT EXISTS 'cdss_user'@'localhost' IDENTIFIED BY 'cdss_password';
GRANT ALL PRIVILEGES ON cdss_db.* TO 'cdss_user'@'localhost';
FLUSH PRIVILEGES;

-- 데이터베이스 확인
USE cdss_db;
SHOW TABLES;

SELECT '데이터베이스 설정 완료!' AS status;
