#!/usr/bin/env python3

import sys
import rethinkdb as r
import bottle as b
import bcrypt as bc

import rethinkserver

PORT = 8080

def get_tpl_vars():
	tpl_vars = TPL_VARS.copy()

	results = list(r.table("twbot").run(conn))
	if results:
		is_first_run = results[0].get("is_first_run")

	tpl_vars["is_first_run"] = is_first_run

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
		}).run(conn)

		print("done")

	if "users" not in r.table_list().run(conn):
		print("creating users table... ", end="", flush=True)
		r.table_create("users").run(conn)
		print("done")

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
}

init_db()

app = b.Bottle()

@app.get("/static/<filepath:path>")
def static_file(filepath):
    return b.static_file(filepath, root="static")

@app.get("/")
@b.view("index.tpl")
def index():
	return get_tpl_vars()

# TODO: require admin authentication
@app.get("/reset-db")
def reset_db():
	init_db(reset=True)

app.run(port=PORT, reloader=True, debug=True)
