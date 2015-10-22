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
	"is_first_run": None,
	"first_run_step": None,
}

def get_tpl_vars():
	tpl_vars = TPL_VARS.copy()

	results = list(r.table("twbot").run(conn))
	if results:
		data = results[0]
		tpl_vars["is_first_run"] = data.get("is_first_run")
		tpl_vars["first_run_step"] = data.get("first_run_step")

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

	if "twbot" not in r.table_list().run(conn):
		print("creating twbot table... ", end="", flush=True)
		r.table_create("twbot").run(conn)
		r.table("twbot").insert({
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
	# TODO: split these actions up into specific functions
	if not get_tpl_vars()["is_first_run"] or get_tpl_vars()["first_run_step"] != 0:
		return

	username = b.request.POST.get("username")
	password = b.request.POST.get("password")

	r.table("users").insert({
		"admin": True,
		"username": username,
		"password": bc.hashpw(password.encode(), salt=bc.gensalt(SALT_ROUNDS)),
	}).run(conn)

	r.table("twbot").update({"first_run_step": 1}).run(conn)
	b.redirect("/")

# TODO: require admin authentication
@app.get("/reset-db")
def reset_db():
	init_db(reset=True)
	b.redirect("/")

app.run(port=PORT, reloader=True, debug=True)
