# syntax = docker/dockerfile:1.2

# Prepare the base environment.
FROM dbcawa/gis_kaartdijin_boodja:latest as builder_base_pbsv2_dev
USER root
RUN --mount=type=cache,target=/var/cache/apt apt-get update && \
    apt-get install --no-install-recommends -y patch libpq-dev git ssh sudo screen virtualenv graphviz python3-pydot && \
    openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 -subj  "/C=AU/ST=Western Australia/L=Perth/O=Development Environment/OU=IT Department/CN=example.com"  -keyout /etc/ssl/private/selfsignedssl.key -out /etc/ssl/private/selfsignedssl.crt && \
    echo 'if ! [ -n "${SUDO_USER}" -a -n "${SUDO_PS1}" ]; then' >> /etc/bash.bashrc && \
    echo "export PS1='\[\e[0;31mdev:\e[0;32m \u@\h:~ \e[0;34m\W\$\e\[\e[0m\] '" >> /etc/bash.bashrc && \
    echo "fi" >> /etc/bash.bashrc

# For windows
# RUN groupadd -g 1000 docker && \
#     useradd -g 1000 -u 10000 docker -s /bin/bash && \
#     mkdir /home/docker && \
#     chown docker.docker /home/docker && \
#     cp /root/.bashrc /home/docker && \
#     cp /root/.profile /home/docker

# For Linux
RUN groupadd -g 20000 container && \
    useradd -g 20000 -u 200000 container -s /bin/bash && \
    mkdir /home/container && \
    chown container.container /home/container && \
    cp /root/.bashrc /home/container && \
    cp /root/.profile /home/container

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
