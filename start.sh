#!/bin/sh

# TODO: Make user able to set the task and job db's here, or use the config.ini
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
TIME=`date`
echo "$TIME - connected successfully"

# TODO: Make user and password settable through environment variable?  
simcity init -u simcityadmin -p simcity &&
  exec python -m bottle scripts.app --bind 0.0.0.0:9090 -s gevent
