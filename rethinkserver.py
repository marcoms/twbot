#!/usr/bin/env python3

import subprocess as sp
import time
import sys

DRIVER_PORT = 8193
ADMIN_PORT = 8194

if __name__ == "__main__":
	print("launching rethinkdb...")
	process = sp.Popen(["rethinkdb", "--http-port", str(ADMIN_PORT), "--driver-port", str(DRIVER_PORT)])

	try:
		while True:
			time.sleep(1)
			if process.poll():
				sys.exit(1)
	except KeyboardInterrupt:
		sys.exit(1)
