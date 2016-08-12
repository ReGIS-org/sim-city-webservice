#!/bin/sh

. env/bin/activate
while ! curl -s http://taskdb:5984/
do
  echo "Waiting for task db..."
  sleep 1
done
while ! curl -s http://jobdb:5984/
do
  echo "Waiting for job db..."
  sleep 1
done
echo "$(date) - connected successfully"

simcity init -u simcityadmin -p simcity &&
  exec python -m bottle scripts.app --bind 0.0.0.0:9090 -s gevent
