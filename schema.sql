
DROP TABLE IF EXISTS history;

CREATE TABLE history
(id INTEGER PRIMARY KEY AUTOINCREMENT,
 reference TEXT,
 app TEXT,
 data TEXT
);

CREATE UNIQUE INDEX history_app_reference ON history(app, reference);
