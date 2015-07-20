# Web interface to SIM-CITY

Contains a Python JSON webservice for a SIM-CITY webserver. It uses the API from [SIM-CITY client](https://github.com/NLeSC/sim-city-client) to create simulation tasks, start new pilot jobs on computing infrastructure and query the status of the simulations and jobs.

## Building and deployment

Following the SIM-CITY client API, a `./config.ini` file should be created containing the configuration of the CouchDB service that will keep the administration of the tasks and jobs, and the type of simulations that can be served. The `config.ini.dist` file can be used as a template for this.

Install by calling `make install` and serve on port 9090 using `make serve`.

## Building and deployment with Docker

With docker, services are compartmentalized and installations standardized. First, configuration files need to be put in place.

1. CouchDB: `docker/couchdb/local.ini` can be edited from `docker/couchdb/local.ini-dist`. Put the admin user here, and set them as environment variables `export COUCHDB_USERNAME='<username>'` and `export COUCHDB_PASSWORD='<password>'`.
2. Osmium: `docker/osmium/joblauncher.yml` can be edited from `docker/osmium/joblauncher.yml-dist`. Configure all hosts that jobs should be submitted to here. Also create an SSH key `ssh-keygen -f docker/osmium/ssh_key -N ""`, and create the right SSH config to SSH to the host in `docker/osmium/ssh_config`, and any mandatory known hosts in `docker/osmium/ssh_known_hosts`. See also [docker-osmium repository](https://github.com/NLeSC/docker-osmium).
3. SIM-CITY webservice: `docker/webservice/config.ini` can be edited from `docker/webservice/config.ini-dist`. Put the configured CouchDB and Osmium information here.

To run the docker components, run

    make docker-run

The web-service is accessible from port 9090, the CouchDB server on port 5984.

Before running again, run

    make docker-clean

