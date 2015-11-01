#!/usr/bin/env python3

import sys
import rethinkdb as r
import bottle as b
import bcrypt as bc

import rethinkserver

PORT = 8080
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
	"bc": bc,
	"user": None,
}

def get_twbot_meta():
	results = list(r.table("meta").run(conn))
	if results:
		return results[0]
	else:
		raise RuntimeError("the twbot database is incorrectly structured")

def get_tpl_vars():
	tpl_vars = TPL_VARS.copy()
	meta = get_twbot_meta()

	# remove non-relevant data for templates

	meta.pop("id")
	meta.pop("admin_username")
	meta.pop("admin_password")

	# combine the two dicts
	tpl_vars = {**tpl_vars, **meta}

	return tpl_vars

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

	r.table("meta").limit(1).update({
		"admin_username": username,
		"admin_password": bc.hashpw(password.encode(), salt=bc.gensalt(SALT_ROUNDS)),
	}).run(conn)

	r.table("meta").update({"first_run_step": 1}).run(conn)
	b.redirect("/")

# TODO: require admin authentication
@app.get("/reset-db")
def reset_db():
	init_db(reset=True)
	b.redirect("/")

app.run(port=PORT, reloader=True, debug=True)
