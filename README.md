# Web interface to SIM-CITY

Contains a Python JSON webservice for a SIM-CITY webserver. It uses the API from [SIM-CITY client](https://github.com/NLeSC/sim-city-client) to create simulation tasks, start new pilot jobs on computing infrastructure and query the status of the simulations and jobs. Documentation of the API is in `docs/apiary.html`.

## Building and deployment

Following the SIM-CITY client API, a `./config.ini` file should be created containing the configuration of the CouchDB service that will keep the administration of the tasks and jobs, and the type of simulations that can be served. The `config.ini.dist` file can be used as a template for this.

Install by calling
```
pip install -r requirements.txt .
```
and serve on port 9090 using `make serve`.

## Building and deployment with Docker

With docker, services are compartmentalized and installations standardized. First, configuration files need to be put in place. First run 

    ./configure-docker.py

1. Osmium: edit `docker/osmium/joblauncher.yml`. See also [docker-osmium repository](https://github.com/NLeSC/docker-osmium).
2. SIM-CITY webservice: edit `docker/webservice/config.ini`.

To run the docker components, run

    . couchdb.env
    make docker-run

The web-service is accessible from port 9090, the CouchDB server on port 5984.

Before running again, run

    make docker-clean

## Testing

Install test dependencies with
```
pip install -U ".[test]"
```
Run unit tests with
```
pytest tests
```
and all tests with
```
pytest --flake8
```
The last command requires docker-compose to be installed. To run custom tests, go to the `integration_tests/docker` folder and run `docker-compose up --build`. For more instructions see `integration_tests/docker/README.md`.
