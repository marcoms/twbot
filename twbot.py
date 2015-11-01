#!/usr/bin/env python3

import sys
import rethinkdb as r
import bottle as b
import tweepy as t
import bcrypt
import pickle
from urllib.parse import urlencode
from uuid import uuid4 as uuid

import rethinkserver

PORT = 8192
SALT_ROUNDS = 14

try:
	conn = r.connect(db="twbot", port=rethinkserver.DRIVER_PORT)
except r.errors.ReqlDriverError:
	print("could not connect to rethinkdb server - please launch rethinkserver.py and try again")
	sys.exit(1)

TPL_VARS = {
	"r": r,
	"b": b,
	"conn": conn,
}

def get_twbot_meta():
	results = list(r.table("meta").run(conn))
	if results:
		return results[0]
	else:
		raise RuntimeError("the twbot database is incorrectly structured")

def get_is_logged_in():
	session = get_twbot_meta().get("session")
	cookie_session = b.request.get_cookie("session")

	if None in (session, cookie_session):
		return False

	return session == cookie_session

def get_tpl_vars():
	tpl_vars = TPL_VARS.copy()
	meta = get_twbot_meta()

	# remove non-relevant data for templates

	meta.pop("id")
	meta.pop("admin_password", None)

	# combine the two dicts
	tpl_vars = {**tpl_vars, **meta}

	tpl_vars["is_logged_in"] = get_is_logged_in()

	return tpl_vars

def password_match(password, hashed):
	if isinstance(password, str):
		password = password.encode()
	elif not isinstance(password, bytes):
		raise RuntimeError("password must be either str or bytes")

	return bcrypt.hashpw(password, hashed) == hashed

def init_db(reset=False):
	if reset:
		print("dropping twbot db... ", end="", flush=True)
		r.db_drop("twbot").run(conn)
		print("done")

	if "twbot" not in r.db_list().run(conn):
		print("creating twbot db... ", end="", flush=True)
		r.db_create("twbot").run(conn)
		print("done")

	if "meta" not in r.table_list().run(conn):
		print("creating meta table... ", end="", flush=True)
		r.table_create("meta").run(conn)
		r.table("meta").insert({
			"is_first_run": True,
			"first_run_step": 0,
		}).run(conn)

		print("done")

	if "users" not in r.table_list().run(conn):
		print("creating users table... ", end="", flush=True)
		r.table_create("users").run(conn)
		print("done")

init_db()

app = b.Bottle()

@app.get("/static/<filepath:path>")
def static_file(filepath):
	return b.static_file(filepath, root="static")

@app.get("/")
@b.view("index.tpl")
def index():
	return get_tpl_vars()

@app.post("/register")
def register():
	meta = get_twbot_meta()
	if not meta["is_first_run"] or meta["first_run_step"] != 0:
		return

	username = b.request.POST.get("username")
	password = b.request.POST.get("password")

	r.table("meta").update({
		"admin_username": username,
		"admin_password": bcrypt.hashpw(password.encode(), salt=bcrypt.gensalt(SALT_ROUNDS)),
	}).run(conn)

	r.table("meta").update({"first_run_step": 1}).run(conn)
	b.redirect("/")

@app.post("/register-tokens")
def register_tokens():
	meta = get_twbot_meta()
	if not meta["is_first_run"] or meta["first_run_step"] != 1:
		return

	api_key = b.request.POST.get("api-key")
	api_secret = b.request.POST.get("api-secret")

	auth = t.OAuthHandler(api_key, api_secret)
	try:
		auth_url = auth.get_authorization_url()
	except t.TweepError:
		print("failed to get autorization url")
		b.redirect("/?" + urlencode({"message": "One or more of these fields were incorrect"}))
		return

	r.table("meta").update({
		"first_run_step": 2,
		"api_key": api_key,
		"api_secret": api_secret,
		"auth": pickle.dumps(auth),
		"auth_url": auth_url,
	}).run(conn)

	b.redirect("/")

@app.post("/register-pin")
def register_pin():
	meta = get_twbot_meta()
	if not meta["is_first_run"] or meta["first_run_step"] != 2:
		return

	pin = b.request.POST.get("pin")

	auth = pickle.loads(meta["auth"])
	access_key, access_secret = auth.get_access_token(pin)
	r.table("meta").update({
		"access_key": access_key,
		"access_secret": access_secret,
		"is_first_run": False,
	}).run(conn)

	r.table("meta").replace(r.row.without(["auth", "auth_url", "first_run_step"])).run(conn)
	b.redirect("/")

@app.get("/login")
@b.view("login.tpl")
def login():
	return get_tpl_vars()

@app.post("/login")
def login_post():
	username = b.request.POST.get("username")
	password = b.request.POST.get("password")
	meta = get_twbot_meta()

	valid = True
	if username == meta["admin_username"]:
		if not password_match(password, meta["admin_password"]):
			valid = False
	else:
		valid = False

	if valid:
		session = str(uuid())
		b.response.set_cookie("session", session, httponly=True)
		r.table("meta").update({"session": session}).run(conn)
		b.redirect("/")
	else:
		b.redirect("/login?" + urlencode({"message": "Incorrect login"}))

@app.get("/admin")
@b.view("admin.tpl")
def admin():
	return get_tpl_vars()

@app.post("/logout")
def logout():
	if not get_is_logged_in():
		b.redirect("/")
		return

	b.response.delete_cookie("session")
	r.table("meta").replace(r.row.without("session")).run(conn)
	b.redirect("/")

# TODO: require admin authentication
@app.get("/reset-db")
def reset_db():
	init_db(reset=True)
	b.redirect("/")

app.run(port=PORT, reloader=True, debug=True)
