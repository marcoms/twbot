#!/usr/bin/env python3

import sys
import rethinkdb as r
import bottle as b

import rethinkserver

try:
	conn = r.connect(db="twbot", port=rethinkserver.DRIVER_PORT)
except r.errors.ReqlDriverError:
	print("could not connect to rethinkdb server - please launch rethinkserver.py and try again")
	sys.exit(1)
