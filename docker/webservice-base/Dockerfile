FROM alpine:3.4
MAINTAINER Joris Borgdorff <j.borgdorff@esciencecenter.nl>

# install requirements
RUN apk add --no-cache openjdk7-jre python python-dev py-pip git build-base curl && \
  pip install virtualenv

RUN adduser -D simcity

USER simcity
RUN git clone https://github.com/indodutch/sim-city-webservice.git \
            /home/simcity/sim-city-webservice ################

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
