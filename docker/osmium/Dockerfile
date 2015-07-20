FROM nlesc/osmium:develop

USER root
COPY ./ssh_key /var/lib/osmium/.ssh/id_rsa
COPY ./ssh_key.pub /var/lib/osmium/.ssh/id_rsa.pub
COPY ./ssh_config /var/lib/osmium/.ssh/config
COPY ./ssh_known_hosts /var/lib/osmium/.ssh/known_hosts
COPY ./joblauncher.yml /var/lib/osmium/joblauncher.yml

RUN chown -R osmium:osmium /var/lib/osmium \
  && chmod 0600 /var/lib/osmium/.ssh/id_rsa*

USER osmium

# Make sure that these ports match those in joblauncher.yml
# API port
EXPOSE 9998
# Admin port
EXPOSE 9999
