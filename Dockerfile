#
# Sim City Webservice base image.
#
# This docker image should not be run as is, but used as a base
# for a webservice image with a config.ini
FROM phusion/baseimage:0.9.19
MAINTAINER Berend Weel <b.weel@esciencecenter.nl>

# install requirements
RUN apt-get update && apt-get install -y python python-dev python-pip git build-essential curl && \
  pip install virtualenv

RUN /usr/sbin/useradd -p $(openssl passwd simcity) -d /home/simcity -m --shell /bin/bash simcity

COPY . /home/simcity/sim-city-webservice

RUN chown -R simcity:simcity /home/simcity

USER simcity
WORKDIR /home/simcity/sim-city-webservice

RUN virtualenv env \
  && . env/bin/activate \
  && pip install -U pip \
  && pip install -r requirements.txt

EXPOSE 9090
ENTRYPOINT ["/bin/sh"]
CMD ["/home/simcity/sim-city-webservice/start.sh"]
