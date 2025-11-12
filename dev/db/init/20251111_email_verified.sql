-- usersテーブルにemail_verifiedカラムを追加
ALTER TABLE users
ADD COLUMN email_verified TINYINT(1) DEFAULT 0;
-- email_verificationsテーブルを作成
CREATE TABLE IF NOT EXISTS email_verifications (
    id CHAR(26) PRIMARY KEY,
    -- ULIDは26文字固定
    user_id VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- イベントスケジューラを使って、期限切れデータを1時間ごとに削除
CREATE EVENT IF NOT EXISTS delete_expired_email_verifications ON SCHEDULE EVERY 1 HOUR DO
DELETE FROM email_verifications
WHERE expires_at < NOW();