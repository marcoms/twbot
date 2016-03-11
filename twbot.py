#!/usr/bin/env python3

# © 2016 Marco Scannadinari <m@scannadinari.co.uk>

import sys
import pickle
import sqlite3 as sqlite
from urllib.parse import urlencode
from uuid import uuid4 as uuid

try:
	import bottle as b
	import tweepy as t
	import bcrypt
	from docopt import docopt
except ImportError as error:
	print(str(error) + "\ncouldn't import all modules. Are all dependencies available?")
	sys.exit(1)

__doc__ = """
twbot - Twitter Quiz Robot

Usage:
  {invok} help
  {invok} [--port <port>]

Options:
  -p <port>, --port <port>  Port to serve web interface at [default: 8080]

Written by Marco Scannadinari
""".format(invok=sys.argv[0]).strip()

req = b.request
resp = b.response

################################################################################
# FUNCTIONS BEGIN ##############################################################

def get_twbot_meta(conn):
	"""
	get the contents of the meta table

	returns a dict-like object of the meta table

	args:
		conn - connection to the database
	"""

	results = conn.execute("SELECT * FROM meta;")
	if results:
		return dict(results.fetchone())
	else:
		raise RuntimeError("the database is incorrectly structured")


def get_is_logged_in(conn):
	"""
	determine if the administrator is logged in

	returns True if logged in

	args:
		conn - connection to the database
	"""

	session = get_twbot_meta(conn).get("session")
	cookie_session = req.get_cookie("session")

	if None in (session, cookie_session):
		return False

	return session == cookie_session


def get_tpl_vars(conn):
	"""
	get variables for templates to use

	returns a dict of variables
	"""

	tpl_vars = TPL_VARS_BASE.copy()
	meta = get_twbot_meta(conn)

	# remove non-relevant data for templates

	meta.pop("id")
	meta.pop("password", None)

	# combine the two dicts
	tpl_vars.update(meta)

	tpl_vars["is_logged_in"] = get_is_logged_in(conn)

	print("template variables:", tpl_vars)

	return tpl_vars


def password_matches(password, hashed):
	"""
	compare a cleartext password to a bcrypt-hashed one

	returns True if the password is a match

	args:
		password - cleartext password
		hashed   - bcrypt-hashed password
	"""


	# polymorphism in action

	if isinstance(password, str):
		password_bytes = password.encode()
	elif isinstance(password, bytes):
		password_bytes = password
	else:
		raise RuntimeError("password must be either str or bytes")

	# bcrypt uses built-in salts, so using the hashed password as the salt
	# parameter will yield the same hashed password if they match
	return bcrypt.hashpw(password_bytes, hashed) == hashed


def get_tables(conn):
	"""
	return a list of tables in the database

	args:
		conn - connection to the database
	"""

	return [element["name"] for element in conn.execute("SELECT name FROM SQLITE_MASTER WHERE type = 'table';")]


def init_db(conn, reset=False):
	"""
	ensure the database has the required tables for twbot

	args:
		conn  - connection to the database
		reset - whether to delete all of the data beforehand [default: False]
	"""

	if reset:
		print("dropping tables...")

		tables = get_tables(conn)

		if "meta" in tables:
			print("dropping meta table... ", end="", flush=True)
			conn.execute("DROP TABLE meta;")
			print("done")

		if "users" in tables:
			print("dropping users table... ", end="", flush=True)
			conn.execute("DROP TABLE users;")
			print("done")

		if "questions" in tables:
			print("dropping questions table... ", end="", flush=True)
			conn.execute("DROP TABLE questions;")
			print("done")

		if "possible_answers" in tables:
			print("dropping possible_answers table... ", end="", flush=True)
			conn.execute("DROP TABLE possible_answers;")
			print("done")

		if "answers" in tables:
			print("dropping answers table... ", end="", flush=True)
			conn.execute("DROP TABLE answers;")
			print("done")

	print("processing meta table... ", end="", flush=True)
	conn.execute(CREATE_META_SQL)

	if not conn.execute("SELECT * FROM meta").fetchone():
		conn.execute(INIT_META_SQL)

	print("done")

	print("processing users table... ", end="", flush=True)
	conn.execute(CREATE_USERS_SQL)
	print("done")

	print("processing questions table... ", end="", flush=True)
	conn.execute(CREATE_QUESTIONS_SQL)
	print("done")

	print("processing possible_answers table... ", end="", flush=True)
	conn.execute(CREATE_POSSIBLE_ANSWERS_SQL)
	print("done")

	print("processing answers table... ", end="", flush=True)
	conn.execute(CREATE_ANSWERS_SQL)
	print("done")

	conn.commit()

	tables = get_tables(conn)
	print("tables:", str(tables))

	conn.commit()

# FUNCTIONS END ################################################################
################################################################################

if __name__ != "__main__":
	print("this is not a library")
	sys.exit(1)

args = docopt(__doc__, help=False)

if args["help"]:
	print(__doc__)
	sys.exit(0)

twbot_port = args["--port"]

try:
	conn = sqlite.connect("twbot.db")
except sqlite.Error as err:
	print(str(err))
	sys.exit(1)

################################################################################
# CONSTANTS BEGIN ##############################################################

CREATE_META_SQL = """CREATE TABLE IF NOT EXISTS meta (
	id INTEGER PRIMARY KEY NOT NULL,
	first_run_step INTEGER NOT NULL,
	api_key TEXT,
	api_secret TEXT,
	access_key TEXT,
	access_secret TEXT,
	username TEXT,
	password BLOB,  -- bcrypt hashed password
	auth BLOB,      -- pickled auth instance
	auth_url TEXT,
	session TEXT
);"""

INIT_META_SQL = "INSERT INTO meta (first_run_step) VALUES (0);"

CREATE_USERS_SQL = """CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY NOT NULL,
	username TEXT NOT NULL
);"""

CREATE_QUESTIONS_SQL = """CREATE TABLE IF NOT EXISTS questions (
	id INTEGER PRIMARY KEY NOT NULL,
	answer_id INTEGER,
	asked_time INTEGER,  -- UNIX time
	question TEXT NOT NULL,
	is_multiple_choice INTEGER NOT NULL,

	FOREIGN KEY(answer_id) REFERENCES possible_answers(id)
);"""

CREATE_POSSIBLE_ANSWERS_SQL = """CREATE TABLE IF NOT EXISTS possible_answers (
	id INTEGER PRIMARY KEY NOT NULL,
	question_id INTEGER NOT NULL,
	letter TEXT NOT NULL,
	answer TEXT NOT NULL,

	FOREIGN KEY(question_id) REFERENCES questions(id)
);"""

CREATE_ANSWERS_SQL = """CREATE TABLE IF NOT EXISTS answers (
	id INTEGER PRIMARY KEY NOT NULL,
	user_id INTEGER NOT NULL,
	question_id INTEGER NOT NULL,
	answer TEXT NOT NULL,
	lag INTEGER NOT NULL,  -- UNIX time

	FOREIGN KEY(user_id) REFERENCES users(id),
	FOREIGN KEY(question_id) REFERENCES questions(id)
);"""

# computational power used for salts. higher values = harder to brute force, slower password hashing
SALT_ROUNDS = 14

TPL_VARS_BASE = {
	"req": req,
	"conn": conn,
}

# CONSTANTS END ################################################################
################################################################################

# allow accessing columns by their name like a dict
conn.row_factory = sqlite.Row

# foreign key constraint support
conn.execute("PRAGMA foreign_keys = ON;")

init_db(conn)

app = b.Bottle()

################################################################################
# ROUTES BEGIN #################################################################

@app.get("/static/<filepath:path>")
def static_file(filepath):
	# correctly handle static file requests
	return b.static_file(filepath, root="static")


@app.get("/")
@b.view("index.tpl")
def index():
	return get_tpl_vars(conn)


@app.post("/register")
def register():
	meta = get_twbot_meta(conn)
	if meta["first_run_step"] != 0:
		return

	username = req.POST.get("username")
	password = req.POST.get("password")

	# form validation

	if not username or not password:
		b.redirect("/?" + urlencode({"message": "Enter both a username and password"}))
	elif len(password) < 5:
		b.redirect("/?" + urlencode({"message": "Password must be at least five characters"}))

	hashed_password = bcrypt.hashpw(password.encode(), salt=bcrypt.gensalt(SALT_ROUNDS))

	# commit admin details and proceed to next step
	conn.execute("""UPDATE meta SET
		username = ?,
		password = ?,
		first_run_step = 1;
	""", (username, hashed_password))

	conn.commit()

	b.redirect("/")


@app.post("/register-tokens")
def register_tokens():
	meta = get_twbot_meta(conn)
	if meta["first_run_step"] != 1:
		return

	api_key = req.POST.get("api-key")
	api_secret = req.POST.get("api-secret")

	auth = t.OAuthHandler(api_key, api_secret)
	try:
		auth_url = auth.get_authorization_url()
	except t.TweepError:
		print("failed to get autorization url")
		b.redirect("/?" + urlencode({"message": "One or more of these fields were incorrect"}))
		return

	conn.execute("""
		UPDATE meta SET
			api_key = ?,
			api_secret = ?,
			auth = ?,
			auth_url = ?,
			first_run_step = 2;
	""", (
		api_key,
		api_secret,
		pickle.dumps(auth),
		auth_url,
	))

	conn.commit()

	b.redirect("/")


@app.post("/register-pin")
def register_pin():
	meta = get_twbot_meta(conn)
	if meta["first_run_step"] != 2:
		return

	pin = req.POST.get("pin")

	auth = pickle.loads(meta["auth"])
	access_key, access_secret = auth.get_access_token(pin)
	conn.execute("""
		UPDATE meta SET
			access_key = ?,
			access_secret = ?,
			auth = NULL,
			auth_url = NULL,
			first_run_step = 3;
	""", (
		access_key,
		access_secret,
	))

	conn.commit()

	b.redirect("/")


@app.post("/finish-setup")
def finish_setup():
	meta = get_twbot_meta(conn)
	if meta["first_run_step"] != 3:
		return

	conn.execute("UPDATE meta SET first_run_step = -1;")
	conn.commit()

	b.redirect("/")


@app.get("/login")
@b.view("login.tpl")
def login():
	return get_tpl_vars(conn)


@app.post("/login")
def login_post():
	username = req.POST.get("username")
	password = req.POST.get("password")
	meta = get_twbot_meta(conn)

	valid = True
	if username == meta["username"]:
		if not password_matches(password, meta["password"]):
			valid = False
	else:
		valid = False

	if valid:
		session = str(uuid())
		resp.set_cookie("session", session, httponly=True)
		conn.execute("UPDATE meta SET session = ?;", (session,))
		conn.commit()

		b.redirect("/")
	else:
		b.redirect("/login?" + urlencode({"message": "Incorrect login"}))


@app.get("/admin")
@b.view("admin.tpl")
def admin():
	return get_tpl_vars(conn)


@app.post("/logout")
def logout():
	if not get_is_logged_in(conn):
		b.redirect("/")
		return

	resp.delete_cookie("session")
	conn.execute("UPDATE meta SET session = NULL;")
	conn.commit()

	b.redirect("/")


# TODO: require admin authentication
@app.get("/achtung-reset")
def reset_db():
	print("resetting dabatase!")
	init_db(conn, reset=True)
	b.redirect("/")

# ROUTES END ###################################################################
################################################################################

app.run(host="0.0.0.0", port=twbot_port, reloader=True, debug=True)
