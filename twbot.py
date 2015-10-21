#!/usr/bin/env python3

import sys
import rethinkdb as r
import bottle as b

import rethinkserver

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
			"first_run": True,
		})

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

init_db()
