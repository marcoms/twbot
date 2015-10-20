#!/usr/bin/env python3

import subprocess as sp

DRIVER_PORT = 8193
ADMIN_PORT = 8194

if __name__ == "__main__":
	print("launching rethinkdb...")
	status = sp.call(["rethinkdb", "--http-port", str(ADMIN_PORT), "--driver-port", str(DRIVER_PORT)])
