#!/bin/bash

if [ "$1" = 'simcity' ]; then
  . env/bin/activate
  export COUCHDB_HOST="${COUCHDB_PORT:6}"
  python env/src/simcity/scripts/createDatabase.py ${COUCHDB_USERNAME:-docker} -p ${COUCHDB_PASSWORD:-docker} &&
    exec python -m bottle scripts.app --bind 0.0.0.0:9090 -s gevent
else
  exec "$@"
fi
