#!/usr/bin/env sh

# start rethinkdb in the background
rethinkdb --http-port 8081 --driver-port 8082 &

./twbot.py
