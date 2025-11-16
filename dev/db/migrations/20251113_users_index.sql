ALTER TABLE users
ADD INDEX users_period_idx (period);
ALTER TABLE users
ADD INDEX users_is_system_idx (is_system);
ALTER TABLE users
ADD INDEX users_is_enable_idx (is_enable);
ALTER TABLE users
ADD INDEX users_is_suspended_idx (is_suspended);
ALTER TABLE users
ADD INDEX users_email_verified_idx (email_verified);
ALTER TABLE users
ADD INDEX users_suspended_until_idx (suspended_until);
ALTER TABLE users
ADD INDEX users_name_idx (name);