CREATE TABLE `users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `custom_id` varchar(255) UNIQUE,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(255) UNIQUE,
  `is_enable` bool
);

CREATE TABLE `apps` (
  `id` varchar(255) PRIMARY KEY DEFAULT 'uuid()',
  `client_id` varchar(255) UNIQUE,
  `client_secret` varchar(255),
  `name` varchar(255),
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `is_enable` bool
);

CREATE TABLE `redirect_uris` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `app_id` varchar(255),
  `uri` varchar(255),
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `auths` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `auth_user_id` int,
  `app_id` varchar(255),
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `is_enable` bool
);

CREATE TABLE `oidc_authorizations` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `auth_id` int,
  `code` int,
  `content` int,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (`content`),
  UNIQUE (`code`)
);

CREATE TABLE `oidc_tokens` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `oidc_authorization_id` int,
  `access_token_id` int,
  `refresh_token_id` int,
  `is_enable` bool,
  UNIQUE (`access_token_id`),
  UNIQUE (`refresh_token_id`),
  UNIQUE (`oidc_authorization_id`)
);

CREATE TABLE `code` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `token` varchar(255),
  `created_at` int,
  `exp` int,
  `is_enable` bool
);

CREATE TABLE `access_tokens` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `hash` varchar(255),
  `type` varchar(255),
  `scope` varchar(255),
  `issued_at` timestamp,
  `exp` timestamp,
  `client_id` int,
  `user_id` int,
  `revoked` bool
);

CREATE TABLE `refresh_tokens` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `hash` varchar(255),
  `type` varchar(255),
  `scope` varchar(255),
  `issued_at` timestamp,
  `exp` timestamp,
  `client_id` int,
  `user_id` int,
  `revoked` bool
);

CREATE TABLE `consents` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `scope` varchar(255),
  `is_enable` bool
);

CREATE TABLE `sessions` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `user_id` int,
  `ip_address` varchar(255),
  `user_agent` varchar(255),
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `is_enable` bool
);

CREATE TABLE `members` (
  `id` varchar(255) PRIMARY KEY DEFAULT 'uuid()',
  `name` varchar(255) NOT NULL,
  `email` varchar(255) UNIQUE,
  `external_email` varchar(255) NOT NULL,
  `custom_id` varchar(255) UNIQUE NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
  `updated_at` timestamp,
  `joined_at` timestamp,
  `is_enable` bool NOT NULL DEFAULT true,
  `period` varchar(255) NOT NULL,
  `system` bool NOT NULL DEFAULT false
);

CREATE TABLE `roles` (
  `id` varchar(255) PRIMARY KEY DEFAULT 'uuid()',
  `custom_id` varchar(255) UNIQUE,
  `permissions` int NOT NULL DEFAULT 0,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
  `updated_at` timestamp,
  `is_enable` bool NOT NULL DEFAULT true,
  `system` bool NOT NULL DEFAULT false
);

CREATE TABLE `discords` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `discord_id` varchar(255) UNIQUE NOT NULL,
  `member` varchar(255) NOT NULL
);

CREATE TABLE `member_role` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `member` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL
);

CREATE TABLE `member_app` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `app` varchar(255),
  `member` varchar(255)
);

ALTER TABLE `members` COMMENT = 'メンバー情報';

ALTER TABLE `roles` COMMENT = 'ロール情報';

ALTER TABLE `users` ADD FOREIGN KEY (`custom_id`) REFERENCES `members` (`custom_id`);

ALTER TABLE `users` ADD FOREIGN KEY (`email`) REFERENCES `members` (`email`);

ALTER TABLE `access_tokens` ADD FOREIGN KEY (`id`) REFERENCES `oidc_tokens` (`refresh_token_id`);

ALTER TABLE `access_tokens` ADD FOREIGN KEY (`id`) REFERENCES `oidc_tokens` (`access_token_id`);

ALTER TABLE `refresh_tokens` ADD FOREIGN KEY (`id`) REFERENCES `oidc_tokens` (`refresh_token_id`);

ALTER TABLE `refresh_tokens` ADD FOREIGN KEY (`id`) REFERENCES `oidc_tokens` (`access_token_id`);

ALTER TABLE `auths` ADD FOREIGN KEY (`auth_user_id`) REFERENCES `users` (`id`);

ALTER TABLE `sessions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `redirect_uris` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`);

ALTER TABLE `auths` ADD FOREIGN KEY (`app_id`) REFERENCES `apps` (`id`);

ALTER TABLE `oidc_authorizations` ADD FOREIGN KEY (`auth_id`) REFERENCES `auths` (`id`);

ALTER TABLE `consents` ADD FOREIGN KEY (`id`) REFERENCES `oidc_authorizations` (`content`);

ALTER TABLE `code` ADD FOREIGN KEY (`id`) REFERENCES `oidc_authorizations` (`code`);

ALTER TABLE `oidc_tokens` ADD FOREIGN KEY (`oidc_authorization_id`) REFERENCES `oidc_authorizations` (`id`);

ALTER TABLE `discords` ADD FOREIGN KEY (`member`) REFERENCES `members` (`id`);

ALTER TABLE `member_role` ADD FOREIGN KEY (`member`) REFERENCES `members` (`id`);

ALTER TABLE `member_role` ADD FOREIGN KEY (`role`) REFERENCES `roles` (`id`);

ALTER TABLE `member_app` ADD FOREIGN KEY (`app`) REFERENCES `apps` (`id`);

ALTER TABLE `member_app` ADD FOREIGN KEY (`member`) REFERENCES `members` (`id`);
