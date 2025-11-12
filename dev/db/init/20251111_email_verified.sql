ALTER TABLE users
ADD COLUMN email_verified TINYINT(1) DEFAULT 0;
CREATE TABLE IF NOT EXISTS email_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    verification_code VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE EVENT delete_expired_email_verifications ON SCHEDULE EVERY 1 HOUR DO
DELETE FROM email_verifications
WHERE expires_at < NOW();