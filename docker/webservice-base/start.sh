#!/bin/bash

. env/bin/activate
# cut off tcp:// from tcp://ip.ad.dr.ss:port
export COUCHDB_HOST="${COUCHDB_PORT:6}"
export OSMIUM_HOST="${OSMIUM_PORT:6}"
if [ -z "$COUCHDB_USERNAME" ]; then
  echo "Warning: COUCHDB_USERNAME not set: using docker"
fi
if [ -z "$COUCHDB_PASSWORD" ]; then
  echo "Warning: COUCHDB_PASSWORD not set: using docker"
fi

while ! curl http://$COUCHDB_HOST/
do
  echo "Waiting for Couchdb..."
  sleep 1
done
echo "$(date) - connected successfully"

python env/src/simcity/scripts/createDatabase.py ${COUCHDB_USERNAME:-docker} -p ${COUCHDB_PASSWORD:-docker} &&
  exec python -m bottle scripts.app --bind 0.0.0.0:9090 -s gevent
