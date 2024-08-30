BEGIN TRANSACTION;
DROP TABLE IF EXISTS `Series`;
CREATE TABLE IF NOT EXISTS `Series` (
	`series_id`	INTEGER NOT NULL UNIQUE,
	`name`	VARCHAR(255) NOT NULL,
	`premiered`	DATETIME,
	`ended`	DATETIME,
	PRIMARY KEY(`series_id` AUTOINCREMENT)
);
DROP TABLE IF EXISTS `ExternalSite`;
CREATE TABLE IF NOT EXISTS `ExternalSite` (
	`externalsite_id`	VARCHAR(10) NOT NULL UNIQUE,
	`name`	VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY(`externalsite_id`)
);
DROP TABLE IF EXISTS `Series_ExternalSite`;
CREATE TABLE IF NOT EXISTS `Series_ExternalSite` (
	`series_id`	INTEGER NOT NULL,
	`externalsite_id`	VARCHAR(10) NOT NULL,
	`value`	VARCHAR(255) NOT NULL,
	`last_update`	INTEGER,
	FOREIGN KEY(`externalsite_id`) REFERENCES `ExternalSite`(`externalsite_id`) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY(`series_id`) REFERENCES `Series`(`series_id`) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY(`series_id`,`externalsite_id`)
);
DROP TABLE IF EXISTS `Episode`;
CREATE TABLE IF NOT EXISTS `Episode` (
	`series_id`	INTEGER NOT NULL,
	`season`	INTEGER NOT NULL,
	`number`	INTEGER NOT NULL,
	`name`	VARCHAR(255) NOT NULL,
	`airstamp`	DATETIME,
	FOREIGN KEY(`series_id`) REFERENCES `Series`(`series_id`) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY(`series_id`,`season`,`number`)
);
DROP TABLE IF EXISTS `Member_Series`;
CREATE TABLE IF NOT EXISTS `Member_Series` (
	`member_id`	INTEGER NOT NULL,
	`series_id`	INTEGER NOT NULL,
	`selected_season`	INTEGER,
	`position`	INTEGER NOT NULL DEFAULT 1,
	FOREIGN KEY(`series_id`) REFERENCES `Series`(`series_id`) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY(`member_id`) REFERENCES `Member`(`member_id`) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY(`member_id`,`series_id`)
);
DROP TABLE IF EXISTS `Member_Episode`;
CREATE TABLE IF NOT EXISTS `Member_Episode` (
	`member_id`	INTEGER NOT NULL,
	`series_id`	INTEGER NOT NULL,
	`season`	INTEGER NOT NULL,
	`number`	INTEGER NOT NULL,
	`status`	SMALLINT NOT NULL DEFAULT 0,
	FOREIGN KEY(`series_id`,`season`,`number`) REFERENCES `Episode`(`series_id`,`season`,`number`) ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY(`member_id`) REFERENCES `Member`(`member_id`) ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY(`member_id`,`series_id`,`season`,`number`)
);
DROP TABLE IF EXISTS `Member`;
CREATE TABLE IF NOT EXISTS `Member` (
	`member_id`	INTEGER NOT NULL UNIQUE,
	`name`	VARCHAR(255) NOT NULL UNIQUE,
	`password`	CHAR(140) NOT NULL,
	PRIMARY KEY(`member_id` AUTOINCREMENT)
);
DROP INDEX IF EXISTS `idx_Series_ExternalSite_externalsite_id_value`;
CREATE INDEX IF NOT EXISTS `idx_Series_ExternalSite_externalsite_id_value` ON `Series_ExternalSite` (
	`externalsite_id`,
	`value`
);
DROP INDEX IF EXISTS `idx_Episode_airdate`;
CREATE INDEX IF NOT EXISTS `idx_Episode_airdate` ON `Episode` (
	`airstamp`
);
DROP INDEX IF EXISTS `idx_Member_Series_member_id_position`;
CREATE INDEX IF NOT EXISTS `idx_Member_Series_member_id_position` ON `Member_Series` (
	`member_id`,
	`position`
);
DROP VIEW IF EXISTS `v_Airdate`;
CREATE VIEW v_Airdate AS
SELECT
	S.series_id,
	S.name AS series_name,
	E.name AS title,
	E.season,
	E.number,
	E.airstamp
FROM Series AS S
	JOIN Episode AS E ON(E.series_id = S.series_id);
DROP VIEW IF EXISTS `v_AirdateMember`;
CREATE VIEW v_AirdateMember AS
SELECT
	MS.member_id,
	MS.position,
	ME.status,
	A.*
FROM v_Airdate AS A
	JOIN Member_Series AS MS ON (MS.series_id = A.series_id)
	LEFT JOIN Member_Episode AS ME ON(
        ME.member_id = MS.member_id AND
        ME.series_id = A.series_id AND
        ME.season = A.season AND
        ME.number = A.number);
DROP VIEW IF EXISTS `v_Following`;
CREATE VIEW v_Following AS
SELECT
    S.series_id AS series_id,
	S.name AS series_name,
    MS.position,
	(SELECT MAX(season) FROM Episode WHERE series_id = S.series_id) AS series_seasons,
    E.season, E.number, E.name AS title, E.airstamp,
    ME.status,
	MS.member_id
FROM Member_Series AS MS
    JOIN Series AS S ON (S.series_id = MS.series_id)
    LEFT JOIN Episode AS E ON (E.series_id = S.series_id AND E.season = MS.selected_season)
    LEFT JOIN Member_Episode AS ME ON (
        ME.member_id = MS.member_id AND
        ME.series_id = S.series_id AND
        ME.season = E.season AND
        ME.number = E.number);
DROP VIEW IF EXISTS `v_SeriesWithoutWhatnextId`;
CREATE VIEW v_SeriesWithoutWhatnextId AS SELECT S.*
FROM Series AS S
WHERE
	NOT EXISTS (
		SELECT *
		FROM Series_ExternalSite AS S_ES
		WHERE S.series_id = S_ES.series_id
			AND S_ES.externalsite_id = "whatnext");
DROP VIEW IF EXISTS `v_RunningSeries`;
CREATE VIEW v_RunningSeries AS SELECT * FROM Series WHERE ended IS NULL;
COMMIT;
