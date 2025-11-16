CREATE TABLE
  `users` (
    `id` VARCHAR(255) PRIMARY KEY,
    `custom_id` VARCHAR(255) UNIQUE NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `password_hash` VARCHAR(255) NULL,
    `email` VARCHAR(255) UNIQUE NOT NULL,
    `external_email` VARCHAR(255) NOT NULL,
    `email_verified` BOOLEAN DEFAULT FALSE,
    `period` VARCHAR(255) NULL,
    `birthdate` DATE DEFAULT NULL,
    `joined_at` DATETIME NULL,
    `is_system` BOOLEAN DEFAULT FALSE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_enable` BOOLEAN DEFAULT TRUE,
    `is_suspended` BOOLEAN DEFAULT FALSE,
    `suspended_until` DATETIME NULL,
    `suspended_reason` TEXT NULL
  );

CREATE INDEX idx_users_custom_id ON users (custom_id);

CREATE TABLE
  `apps` (
    `id` VARCHAR(255) PRIMARY KEY,
    `client_secret` VARCHAR(255) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_enable` BOOLEAN DEFAULT TRUE
  );

CREATE TABLE
  `redirect_uris` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `app_id` VARCHAR(255) NOT NULL,
    `uri` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

CREATE TABLE
  `auths` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `auth_user_id` VARCHAR(255) NOT NULL,
    `app_id` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `is_enable` BOOLEAN NOT NULL DEFAULT TRUE
  );

CREATE TABLE
  `oidc_authorizations` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `auth_id` INT NOT NULL,
    `code_id` INT NOT NULL,
    `consent_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (`code_id`)
  );

CREATE TABLE
  `token_sets` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `oidc_authorization_id` INT NOT NULL,
    `access_token_id` VARCHAR(255) NOT NULL,
    `refresh_token_id` VARCHAR(255) NOT NULL,
    `id_token_id` VARCHAR(255) NOT NULL,
    `is_enable` BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (`access_token_id`),
    UNIQUE (`refresh_token_id`),
    UNIQUE (`id_token_id`),
    UNIQUE (`oidc_authorization_id`)
  );

CREATE TABLE
  `code` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `token` VARCHAR(255) UNIQUE NOT NULL,
    `nonce` VARCHAR(255) NULL,
    `code_challenge` VARCHAR(255) NULL,
    `code_challenge_method` VARCHAR(255) NULL,
    `acr` VARCHAR(255) NULL,
    `amr` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `exp` TIMESTAMP,
    `is_enable` BOOLEAN NOT NULL DEFAULT TRUE
  );

CREATE TABLE
  `access_tokens` (
    `id` VARCHAR(255) PRIMARY KEY,
    `hash` VARCHAR(255) NOT NULL,
    `type` VARCHAR(255) NOT NULL,
    `scope` VARCHAR(255) NOT NULL,
    `issued_at` TIMESTAMP NOT NULL,
    `exp` TIMESTAMP NOT NULL,
    `client_id` VARCHAR(255) NOT NULL COMMENT 'アプリケーションID',
    `user_id` VARCHAR(255) NOT NULL,
    `revoked` BOOLEAN NOT NULL DEFAULT FALSE
  );

CREATE TABLE
  `refresh_tokens` (
    `id` VARCHAR(255) PRIMARY KEY,
    `hash` VARCHAR(255) NOT NULL,
    `type` VARCHAR(255) NOT NULL,
    `issued_at` TIMESTAMP NOT NULL,
    `exp` TIMESTAMP NOT NULL,
    `client_id` VARCHAR(255) NOT NULL COMMENT 'アプリケーションID',
    `user_id` VARCHAR(255) NOT NULL,
    `revoked` BOOLEAN NOT NULL DEFAULT FALSE
  );

CREATE TABLE
  `id_tokens` (
    `id` VARCHAR(255) PRIMARY KEY,
    `hash` VARCHAR(255) NOT NULL,
    `type` VARCHAR(255) NOT NULL,
    `issued_at` TIMESTAMP NOT NULL,
    `exp` TIMESTAMP NOT NULL,
    `client_id` VARCHAR(255) NOT NULL COMMENT 'アプリケーションID',
    `nonce` VARCHAR(255) NULL,
    `auth_time` TIMESTAMP NULL,
    `acr` VARCHAR(255) NULL,
    `amr` VARCHAR(255) NULL,
    -- JSONでもよい
    `user_id` VARCHAR(255) NOT NULL,
    `revoked` BOOLEAN NOT NULL DEFAULT FALSE
  );

CREATE TABLE
  `consents` (`id` INT PRIMARY KEY AUTO_INCREMENT, `scope` VARCHAR(255), `is_enable` BOOLEAN);

CREATE TABLE
  `sessions` (
    `id` VARCHAR(255) PRIMARY KEY,
    `user_id` VARCHAR(255) NOT NULL,
    `ip_address` VARCHAR(255) NOT NULL,
    `user_agent` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `expires_at` TIMESTAMP,
    `is_enable` BOOLEAN NOT NULL DEFAULT TRUE
  );

CREATE TABLE
  `roles` (
    `id` VARCHAR(255) PRIMARY KEY,
    `custom_id` VARCHAR(255) UNIQUE NOT NULL,
    `name` VARCHAR(255) NULL,
    `permission` INT NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    `is_enable` BOOLEAN DEFAULT TRUE,
    `is_system` BOOLEAN DEFAULT FALSE
  );

CREATE TABLE
  `discords` (`id` INT PRIMARY KEY AUTO_INCREMENT, `discord_id` VARCHAR(255) UNIQUE NOT NULL, `user_id` VARCHAR(255) NOT NULL);

CREATE TABLE
  `user_role` (`id` INT PRIMARY KEY AUTO_INCREMENT, `user_id` VARCHAR(255) NOT NULL, `role_id` VARCHAR(255) NOT NULL);

CREATE TABLE
  `user_app` (`id` INT PRIMARY KEY AUTO_INCREMENT, `app_id` VARCHAR(255), `user_id` VARCHAR(255));

CREATE TABLE
  `email_verifications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` VARCHAR(255) NOT NULL,
    `verification_code` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `expires_at` DATETIME NOT NULL
  );

ALTER TABLE `roles` COMMENT = 'ロール情報';

ALTER TABLE `token_sets` ADD FOREIGN KEY (`access_token_id`) REFERENCES `access_tokens` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `token_sets` ADD FOREIGN KEY (`refresh_token_id`) REFERENCES `refresh_tokens` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `token_sets` ADD FOREIGN KEY (`id_token_id`) REFERENCES `id_tokens` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `auths` ADD FOREIGN KEY (`auth_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `sessions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `redirect_uris` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `auths` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `oidc_authorizations` ADD FOREIGN KEY (`auth_id`) REFERENCES `auths` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `oidc_authorizations` ADD FOREIGN KEY (`consent_id`) REFERENCES `consents` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `oidc_authorizations` ADD FOREIGN KEY (`code_id`) REFERENCES `code` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `token_sets` ADD FOREIGN KEY (`oidc_authorization_id`) REFERENCES `oidc_authorizations` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `discords` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `user_role` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `user_role` ADD FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `user_app` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `user_app` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;