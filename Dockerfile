#
# Sim City Webservice base image.
#
# This docker image should not be run as is, but used as a base
# for a webservice image with a config.ini
FROM alpine:3.4
MAINTAINER Berend Weel <b.weel@esciencecenter.nl>

# install requirements
RUN apk add --no-cache openjdk7-jre python python-dev py-pip git build-base curl && \
  pip install virtualenv

COPY . /home/simcity/sim-city-webservice

RUN adduser -D simcity
RUN chown -R simcity:simcity /home/simcity

USER simcity
WORKDIR /home/simcity/sim-city-webservice

RUN virtualenv env \
  && . env/bin/activate \
  && pip install -U pip \
  && pip install -r requirements.txt

USER root
COPY start.sh /start.sh
RUN chown -R simcity:simcity /home/simcity

USER simcity
EXPOSE 9090
ENTRYPOINT ["/bin/sh"]
CMD ["/start.sh"]
