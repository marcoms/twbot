# © 2016 Marco Scannadinari <m@scannadinari.co.uk>

# sql statements to be executed by twbot

# INTEGERs designated as booleans follow the pattern that 1 = True, 0 = False

import sys

CREATE_META = """CREATE TABLE IF NOT EXISTS meta (
	id INTEGER PRIMARY KEY NOT NULL,

	first_run_step INTEGER NOT NULL,
	api_key TEXT,
	api_secret TEXT,
	access_key TEXT,
	access_secret TEXT,
	username TEXT,

	-- bcrypt hashed password
	password BLOB,

	session TEXT
);"""

INIT_META = "INSERT INTO meta (first_run_step) VALUES (0);"

CREATE_PLAYERS = """CREATE TABLE IF NOT EXISTS players (
	id INTEGER PRIMARY KEY NOT NULL
);"""

CREATE_QUESTIONS = """CREATE TABLE IF NOT EXISTS questions (
	id INTEGER PRIMARY KEY NOT NULL,

	possible_answer_id INTEGER,

	-- UNIX time
	ask_time INTEGER NOT NULL,

	-- boolean
	is_asked INTEGER NOT NULL DEFAULT 0,

	question TEXT NOT NULL,

	FOREIGN KEY(possible_answer_id) REFERENCES possible_answers(id)
);"""

CREATE_POSSIBLE_ANSWERS = """CREATE TABLE IF NOT EXISTS possible_answers (
	id INTEGER PRIMARY KEY NOT NULL,

	question_id INTEGER NOT NULL,
	letter TEXT NOT NULL,
	answer TEXT NOT NULL,

	FOREIGN KEY(question_id) REFERENCES questions(id)
);"""

CREATE_ANSWERS = """CREATE TABLE IF NOT EXISTS answers (
	id INTEGER PRIMARY KEY NOT NULL,

	player_id INTEGER NOT NULL,
	question_id INTEGER NOT NULL,
	possible_answer_id INTEGER,
	answer TEXT NOT NULL,

	-- UNIX time
	time INTEGER NOT NULL,

	score INTEGER,
	comment TEXT,

	dm_id INTEGER NOT NULL,

	-- boolean
	messaged_score INTEGER NOT NULL,

	FOREIGN KEY(dm_id) REFERENCES dms(id),
	FOREIGN KEY(player_id) REFERENCES players(id),
	FOREIGN KEY(question_id) REFERENCES questions(id),
	FOREIGN KEY(possible_answer_id) REFERENCES possible_answers(id)
);"""

CREATE_DMS = """CREATE TABLE IF NOT EXISTS dms (
	id INTEGER PRIMARY KEY NOT NULL
);"""

CREATE_MENTIONS = """CREATE TABLE IF NOT EXISTS mentions (
	id INTEGER PRIMARY KEY NOT NULL
);"""

if __name__ == "__main__":
	print("this is not a program")
	sys.exit(1)