# Web interface to SIM-CITY

Contains a Python JSON webservice for a SIM-CITY webserver. It uses the API from [SIM-CITY client](https://github.com/NLeSC/sim-city-client) to create simulation tasks, start new pilot jobs on computing infrastructure and query the status of the simulations and jobs.

## Building and deployment

Following the SIM-CITY client API, a `./config.ini` file should be created containing the configuration of the CouchDB service that will keep the administration of the tasks and jobs, and the type of simulations that can be served. The `config.ini.dist` file can be used as a template for this.

Install by calling `make install` and serve using `make serve`.
