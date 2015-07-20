#!/bin/bash

. env/bin/activate
# cut off tcp:// from tcp://ip.ad.dr.ss:port
export COUCHDB_HOST="${COUCHDB_PORT:6}"
export OSMIUM_HOST="${OSMIUM_PORT:6}"
echo ${COUCHDB_USERNAME:-docker}
echo ${COUCHDB_PASSWORD:-docker}
python env/src/simcity/scripts/createDatabase.py ${COUCHDB_USERNAME:-docker} -p ${COUCHDB_PASSWORD:-docker} &&
  exec python -m bottle scripts.app --bind 0.0.0.0:9090 -s gevent
