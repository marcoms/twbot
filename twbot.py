#!/usr/bin/env python3

try:
	import sys
	import rethinkdb as r
	import bottle as b
	import tweepy as t
	import bcrypt
	import pickle
	from urllib.parse import urlencode
	from uuid import uuid4 as uuid
except ImportError as error:
	print(str(error) + "\ncouldn't import all modules. Are all dependencies available?")
	sys.exit(1)

if __name__ != "__main__":
	print("this is not a library")
	sys.exit(1)


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
	tpl_vars.update(meta)

	tpl_vars["is_logged_in"] = get_is_logged_in()

	return tpl_vars


def password_match(password, hashed):
	if isinstance(password, str):
		password = password.encode()
	elif not isinstance(password, bytes):
		raise RuntimeError("password must be either str or bytes")

	# bcrypt uses built-in salts, so using the hashed password as the salt parameter should yield the same hashed password if they match
	return bcrypt.hashpw(password, hashed) == hashed


def init_db(reset=False):
	if reset:
		if "twbot" in r.db_list().run(conn):
			if "meta" in r.table_list().run(conn):
				print("resetting meta table... ", end="", flush=True)
				r.table("meta").delete().run(conn)
				r.table("meta").insert(META_DEFAULTS).run(conn)
				print("done")

			if "users" in r.table_list().run(conn):
				print("resetting users table... ", end="", flush=True)
				r.table("users").delete().run(conn)
				print("done")

	if "twbot" not in r.db_list().run(conn):
		print("creating twbot db... ", end="", flush=True)
		r.db_create("twbot").run(conn)
		print("done")

	if "meta" not in r.table_list().run(conn):
		print("creating meta table... ", end="", flush=True)
		r.table_create("meta").run(conn)
		r.table("meta").insert(META_DEFAULTS).run(conn)

		print("done")

	if "users" not in r.table_list().run(conn):
		print("creating users table... ", end="", flush=True)
		r.table_create("users").run(conn)
		print("done")

# various constants to be used later

SALT_ROUNDS = 14
META_DEFAULTS = {
	"is_first_run": True,
	"first_run_step": 0,
}

twbot_port = sys.argv[1] if len(sys.argv) > 1 else 8080
rethink_driver_port = sys.argv[2] if len(sys.argv) > 2 else None

try:
	if rethink_driver_port:
		conn = r.connect(db="twbot", port=rethink_driver_port)
	else:
		conn = r.connect(db="twbot")
except r.errors.ReqlDriverError:
	print("could not connect to rethinkdb server")
	sys.exit(1)

TPL_VARS = {
	"r": r,
	"b": b,
	"conn": conn,
}

init_db()

app = b.Bottle()


@app.get("/static/<filepath:path>")
def static_file(filepath):
	# correctly handle static file requests

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

	# form validation

	if not username or not password:
		b.redirect("/?" + urlencode({"message": "Enter both a username and password"}))
	elif len(password) < 5:
		b.redirect("/?" + urlencode({"message": "Password must be at least five characters"}))

	# commit admin details
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

		# the authorisation session is stored in the instance so we have to serialise it to the database for future availabliity
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
		"first_run_step": 3,
	}).run(conn)

	r.table("meta").replace(r.row.without(["auth", "auth_url"])).run(conn)
	b.redirect("/")


@app.post("/finish-setup")
def finish_setup():
	meta = get_twbot_meta()
	if not meta["is_first_run"] or meta["first_run_step"] != 3:
		return

	r.table("meta").update({"is_first_run": False}).run(conn)
	r.table("meta").replace(r.row.without("first_run_step")).run(conn)

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

app.run(port=twbot_port, reloader=True, debug=True)
