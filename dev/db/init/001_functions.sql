DELIMITER //

CREATE FUNCTION to_crockford_b32 (src BIGINT, encoded_len INT)
RETURNS TEXT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE result TEXT DEFAULT '';
    DECLARE b32char CHAR(32) DEFAULT '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
    DECLARE i INT DEFAULT 0;

ENCODE: LOOP
        SET i = i + 1;
        SET result = CONCAT(SUBSTRING(b32char, (src MOD 32) + 1, 1), result);
        SET src = src DIV 32;

        IF i < encoded_len THEN
            ITERATE ENCODE;
        END IF;

        LEAVE ENCODE;
END LOOP ENCODE;

RETURN result;
END//

CREATE FUNCTION gen_ulid ()
RETURNS CHAR(26)
NOT DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE msec_ts BIGINT DEFAULT FLOOR(UNIX_TIMESTAMP(CURRENT_TIMESTAMP(4)) * 1000);
    DECLARE rand CHAR(20) DEFAULT HEX(RANDOM_BYTES(10));
    DECLARE rand_first BIGINT DEFAULT CONV(SUBSTRING(rand, 1, 10), 16, 10);
    DECLARE rand_last  BIGINT DEFAULT CONV(SUBSTRING(rand, 11, 10), 16, 10);

    RETURN CONCAT(
        to_crockford_b32(msec_ts, 10),
        to_crockford_b32(rand_first, 8),
        to_crockford_b32(rand_last, 8)
    );
END//

CREATE TRIGGER before_insert_users
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = gen_ulid();
    END IF;
END//

CREATE TRIGGER before_insert_apps
BEFORE INSERT ON apps
FOR EACH ROW
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = gen_ulid();
    END IF;
END//

CREATE TRIGGER before_insert_roles
BEFORE INSERT ON roles
FOR EACH ROW
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = gen_ulid();
    END IF;
END//

CREATE TRIGGER before_insert_sessions
BEFORE INSERT ON sessions
FOR EACH ROW
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = gen_ulid();
    END IF;
END//

DELIMITER ;

SET GLOBAL event_scheduler = ON;

CREATE EVENT delete_expired_sessions
ON SCHEDULE EVERY 1 HOUR
DO
    DELETE FROM sessions WHERE expires_at < NOW();
