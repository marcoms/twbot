#!/usr/bin/env sh

# start rethinkdb and twbot in the background

rethinkdb --http-port 8081 --driver-port 8082 &
./twbot.py &

# loop until SIGINT et al

yes > /dev/null
