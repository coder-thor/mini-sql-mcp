-- sqlite3 demo.sqlite < demo.sql
-- 业务表和第 7 节一样。用户表、会话表不放进来。

CREATE TABLE characters (
    name TEXT PRIMARY KEY,
    rank INTEGER NOT NULL,
    element TEXT NOT NULL,
    weapon_type TEXT NOT NULL
);

CREATE TABLE weapons (
    name TEXT PRIMARY KEY,
    rank INTEGER NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE artifacts (
    name TEXT PRIMARY KEY,
    effects TEXT NOT NULL
);

CREATE TABLE weapon_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_name TEXT NOT NULL,
    weapon_name TEXT NOT NULL,
    UNIQUE (character_name, weapon_name)
);

CREATE TABLE artifact_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_name TEXT NOT NULL,
    set_name TEXT NOT NULL,
    UNIQUE (character_name, set_name)
);

INSERT INTO characters VALUES ('米提亚', 5, 'Electric', 'WEAPON_CATALYST');
INSERT INTO weapons VALUES ('神乐之真意', 5, 'WEAPON_CATALYST');
INSERT INTO weapons VALUES ('天空之卷', 5, 'WEAPON_CATALYST');
INSERT INTO weapon_recommendations (character_name, weapon_name) VALUES ('米提亚', '神乐之真意');
INSERT INTO weapon_recommendations (character_name, weapon_name) VALUES ('米提亚', '天空之卷');
