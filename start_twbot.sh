#!/usr/bin/env sh

# launch rethinkdb in the background
rethinkdb --http-port 8081 --driver-port 8082 &

./twbot.py
