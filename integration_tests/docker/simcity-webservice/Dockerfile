FROM simcity-webservice-base
MAINTAINER Berend Weel <b.weel@esciencecenter.nl>

WORKDIR /home/simcity/sim-city-webservice

USER root
COPY config.ini /home/simcity/sim-city-webservice/config.ini
COPY test_simulation.json /home/simcity/sim-city-webservice/simulations/test_simulation.json

RUN chown -R simcity:simcity /home/simcity