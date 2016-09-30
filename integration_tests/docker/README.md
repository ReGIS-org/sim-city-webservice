# Test services with docker-compose

First, install docker-compose. Then, run a test infrastructure with
```
docker-compose up --build -d
```
The sim-city-webservice is now available on localhost port 9098. There are two CouchDB databases running, a task database on port 5784 and a job database on port 5884 (user simcityadmin, password simcity).  A webdav server is running on port 8080 (user webdav, password vadbew).  And finally, a Slurm cluster is accessible over SSH on port 10022 (user `xenon`, password `javagat`).

These tests are based on the ones in [Xenon](http://nlesc.github.io/Xenon).
