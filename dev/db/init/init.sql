CREATE TABLE `users` (
    `id` varchar(255) PRIMARY KEY,
    `custom_id` VARCHAR(255) UNIQUE NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `password_hash` VARCHAR(255) NULL,
    `email` VARCHAR(255) UNIQUE NOT NULL,
    `external_email` VARCHAR(255) NOT NULL,
    `period` VARCHAR(255) NULL,
    `joined_at` DATETIME NULL,
    `is_system` BOOLEAN DEFAULT FALSE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_enable` BOOLEAN DEFAULT TRUE,
    `is_suspended` BOOLEAN DEFAULT FALSE,
    `suspended_until` DATETIME NULL,
    `suspended_reason` TEXT NULL
);

CREATE INDEX idx_users_custom_id ON users(custom_id);
CREATE TABLE `apps` (
  `id` varchar(255) PRIMARY KEY,
  `client_secret` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_enable` BOOLEAN DEFAULT true
);

CREATE TABLE `redirect_uris` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `app_id` varchar(255) NOT NULL,
  `uri` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `auths` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `auth_user_id` varchar(255) NOT NULL,
  `app_id` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `is_enable` BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE `oidc_authorizations` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `auth_id` int NOT NULL,
  `code_id` int NOT NULL,
  `consent_id` int NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (`code_id`)
);

CREATE TABLE `token_sets` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `oidc_authorization_id` int NOT NULL,
  `access_token_id` varchar(255) NOT NULL,
  `refresh_token_id` varchar(255) NOT NULL,
  `id_token_id` varchar(255) NOT NULL,
  `is_enable` BOOLEAN NOT NULL DEFAULT true,
  UNIQUE (`access_token_id`),
  UNIQUE (`refresh_token_id`),
  UNIQUE (`id_token_id`),
  UNIQUE (`oidc_authorization_id`)
);

CREATE TABLE `code` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `token` varchar(255) UNIQUE NOT NULL,
  `nonce` varchar(255) NULL,
  `code_challenge` varchar(255) NULL,
  `code_challenge_method` varchar(255) NULL,
  `acr` varchar(255) NULL,
  `amr` varchar(255) NULL,  -- JSONでもよい
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `exp` timestamp,
  `is_enable` BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE `access_tokens` (
    `id` varchar(255) PRIMARY KEY,
  `hash` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `scope` varchar(255) NOT NULL,
  `issued_at` timestamp NOT NULL,
  `exp` timestamp NOT NULL,
  `client_id` varchar(255) NOT NULL COMMENT 'アプリケーションID',
  `user_id` varchar(255) NOT NULL,
  `revoked` BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE `refresh_tokens` (
  `id` varchar(255) PRIMARY KEY,
  `hash` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `issued_at` timestamp NOT NULL,
  `exp` timestamp NOT NULL,
  `client_id` varchar(255) NOT NULL COMMENT 'アプリケーションID',
  `user_id` varchar(255) NOT NULL,
  `revoked` BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE `id_tokens` (
  `id` varchar(255) PRIMARY KEY,
  `hash` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `issued_at` timestamp NOT NULL,
  `exp` timestamp NOT NULL,
  `client_id` varchar(255) NOT NULL COMMENT 'アプリケーションID',
  `aud` varchar(255) NOT NULL,
  `nonce` varchar(255) NULL,
  `auth_time` timestamp NULL,
  `acr` varchar(255) NULL,
  `amr` varchar(255) NULL,  -- JSONでもよい
  `user_id` varchar(255) NOT NULL,
  `revoked` BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE `consents` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `scope` varchar(255),
  `is_enable` BOOLEAN
);

CREATE TABLE `sessions` (
  `id` varchar(255) PRIMARY KEY,
  `user_id` varchar(255) NOT NULL,
  `ip_address` varchar(255) NOT NULL,
  `user_agent` varchar(255) NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `expires_at` timestamp,
  `is_enable` BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE `roles` (
  `id` varchar(255) PRIMARY KEY,
  `custom_id` varchar(255) UNIQUE NOT NULL,
  `name` varchar(255) NULL,
  `permission` int NOT NULL DEFAULT 0,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
  `is_enable` BOOLEAN DEFAULT true,
  `is_system` BOOLEAN DEFAULT false
);

CREATE TABLE `discords` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `discord_id` varchar(255) UNIQUE NOT NULL,
  `user_id` varchar(255) NOT NULL
);

CREATE TABLE `user_role` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL,
  `role_id` varchar(255) NOT NULL
);

CREATE TABLE `user_app` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `app_id` varchar(255),
  `user_id` varchar(255)
);

ALTER TABLE `roles` COMMENT = 'ロール情報';

ALTER TABLE `token_sets` ADD FOREIGN KEY (`access_token_id`) REFERENCES `access_tokens` (`id`);

ALTER TABLE `token_sets` ADD FOREIGN KEY (`refresh_token_id`) REFERENCES `refresh_tokens` (`id`);

ALTER TABLE `token_sets` ADD FOREIGN KEY (`id_token_id`) REFERENCES `id_tokens` (`id`);

ALTER TABLE `auths` ADD FOREIGN KEY (`auth_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `sessions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `redirect_uris` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`);

ALTER TABLE `auths` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`);

ALTER TABLE `oidc_authorizations` ADD FOREIGN KEY (`auth_id`) REFERENCES `auths` (`id`);

ALTER TABLE `oidc_authorizations` ADD FOREIGN KEY (`consent_id`) REFERENCES `consents` (`id`);

ALTER TABLE `oidc_authorizations` ADD FOREIGN KEY (`code_id`) REFERENCES `code` (`id`);

ALTER TABLE `token_sets` ADD FOREIGN KEY (`oidc_authorization_id`) REFERENCES `oidc_authorizations` (`id`);

ALTER TABLE `discords` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `user_role` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `user_role` ADD FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`);

ALTER TABLE `user_app` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`);

ALTER TABLE `user_app` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

DELIMITER //
CREATE FUNCTION to_crockford_b32 (src BIGINT, encoded_len INT)
RETURNS TEXT DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE result TEXT DEFAULT '';
  DECLARE b32char CHAR(32) DEFAULT '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
  DECLARE i INT DEFAULT 0;

  ENCODE: LOOP
    SET i = i + 1;
    SET result = CONCAT(SUBSTRING(b32char, (src MOD 32)+1, 1), result);
    SET src = src DIV 32;
    IF i < encoded_len THEN
      ITERATE ENCODE;
    END IF;
    LEAVE ENCODE;
  END LOOP ENCODE;

  RETURN result;
END; //

CREATE FUNCTION gen_ulid ()
RETURNS CHAR(26) NOT DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE msec_ts BIGINT DEFAULT FLOOR(UNIX_TIMESTAMP(CURRENT_TIMESTAMP(4)) * 1000);
  DECLARE rand CHAR(20) DEFAULT HEX(RANDOM_BYTES(10));
  DECLARE rand_first BIGINT DEFAULT CONV(SUBSTRING(rand, 1, 10), 16, 10);
  DECLARE rand_last BIGINT DEFAULT CONV(SUBSTRING(rand, 11, 10), 16, 10);
  RETURN CONCAT(
    to_crockford_b32(msec_ts, 10),
    to_crockford_b32(rand_first, 8),
    to_crockford_b32(rand_last, 8)
  );
END; //

DELIMITER ;

DELIMITER //
CREATE TRIGGER before_insert_users
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
  IF NEW.id IS NULL OR NEW.id = '' THEN
    SET NEW.id = gen_ulid();
  END IF;
END; //
DELIMITER ;

DELIMITER //
CREATE TRIGGER before_insert_apps
BEFORE INSERT ON apps
FOR EACH ROW
BEGIN
  IF NEW.id IS NULL OR NEW.id = '' THEN
    SET NEW.id = gen_ulid();
  END IF;
END; //
DELIMITER ;

DELIMITER //
CREATE TRIGGER before_insert_roles
BEFORE INSERT ON roles
FOR EACH ROW
BEGIN
  IF NEW.id IS NULL OR NEW.id = '' THEN
    SET NEW.id = gen_ulid();
  END IF;
END; //
DELIMITER ;

DELIMITER //
CREATE TRIGGER before_insert_sessions
BEFORE INSERT ON sessions
FOR EACH ROW
BEGIN
  IF NEW.id IS NULL OR NEW.id = '' THEN
    SET NEW.id = gen_ulid();
  END IF;
END; //
DELIMITER ;

SET GLOBAL event_scheduler = ON;

CREATE EVENT delete_expired_sessions
ON SCHEDULE EVERY 1 HOUR
DO
  DELETE FROM sessions WHERE expires_at < NOW();
