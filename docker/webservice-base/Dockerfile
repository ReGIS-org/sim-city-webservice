FROM python:2.7
MAINTAINER Joris Borgdorff <j.borgdorff@esciencecenter.nl>

# install requirements
RUN apt-get update -y && apt-get install -y git && apt-get install -y default-jdk

RUN groupadd -r simcity && useradd -d /var/lib/simcity -g simcity simcity \
  && mkdir /var/lib/simcity \
  && chown -R simcity:simcity /var/lib/simcity

USER simcity
# Variable is a workaround to disable cache from this point forward
RUN simcity_commit="646f008914e5b3811e14751e698138bfaab8501e" \
  git clone https://github.com/NLeSC/sim-city-webservice.git \
            /var/lib/simcity/sim-city-webservice

WORKDIR /var/lib/simcity/sim-city-webservice

RUN virtualenv env \
  && . env/bin/activate \
  && pip install -U pip \
  && git checkout develop \
  && simcity_client_commit="d6aab4fced5072a69589a680d50095a7fc9dd051" \
     make install

USER root
COPY /start.sh /
RUN chown simcity:simcity /start.sh && chmod +x /start.sh

USER simcity
EXPOSE 9090
CMD ["/start.sh"]
