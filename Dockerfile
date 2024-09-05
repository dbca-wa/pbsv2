# syntax = docker/dockerfile:1.2

FROM ubuntu:24.04 as builder_base_oim_pbsv2

LABEL maintainer="asi@dbca.wa.gov.au"
LABEL org.opencontainers.image.source="https://github.com/dbca-wa/pbsv2"

ENV DEBIAN_FRONTEND=noninteractive \
    DEB_PYTHON_INSTALL_LAYOUT=deb \
    DEBUG=True \
    TZ=Australia/Perth \
    PRODUCTION_EMAIL=True \
    SECRET_KEY="ThisisNotRealKey" \
    SITE_DOMAIN='dbca.wa.gov.au' \
    BPAY_ALLOWED=False \
    POETRY_VERSION=1.8.3 \
    NODE_MAJOR=20

FROM builder_base_oim_pbsv2 as apt_packages_pbsv2

# Use Australian Mirrors
RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list && \
    mv /etc/apt/sourcesau.list /etc/apt/sources.list

RUN --mount=type=cache,target=/var/cache/apt apt-get update && \
    apt-get upgrade -y && \
    apt-get install --no-install-recommends -y \
    binutils \
    ca-certificates \
    cron \
    curl \
    gdal-bin \
    gnupg \
    gcc \
    git \
    htop \
    libmagic-dev \
    libproj-dev \
    libpq-dev \
    libspatialindex-dev \
    mtr \
    patch \
    postgresql-client \
    python3-dev \
    python3-gdal \
    python3-pip \
    python3-poetry \
    python3-setuptools \
    python3-venv \
    rsyslog \
    software-properties-common \
    sqlite3 \
    ssh \
    sudo \
    tzdata \
    vim \
    wget && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

FROM apt_packages_pbsv2 as node_pbsv2

# install node 20
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" \
    | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs

FROM node_pbsv2 as configure_pbsv2

COPY startup.sh /

RUN chmod 755 /startup.sh && \
    chmod +s /startup.sh && \
    groupadd -g 5000 oim && \
    useradd -g 5000 -u 5000 oim -s /bin/bash -d /app && \
    usermod -a -G sudo oim && \
    echo "oim  ALL=(ALL)  NOPASSWD: /startup.sh" > /etc/sudoers.d/oim && \
    mkdir /app && \
    chown -R oim.oim /app && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/default_script_installer.sh -O /tmp/default_script_installer.sh && \
    chmod 755 /tmp/default_script_installer.sh && \
    /tmp/default_script_installer.sh && \
    rm -rf /tmp/*

FROM configure_pbsv2 as python_dependencies_pbsv2

WORKDIR /app
USER oim

ENV POETRY_HOME=/app/poetry
ENV PATH=$POETRY_HOME/bin:$PATH
COPY --chown=oim:oim pyproject.toml poetry.lock ./
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION
RUN poetry completions bash > ~/.bash_completion && \
    poetry run pip install --upgrade pip
RUN --mount=type=cache,target=~/.cache/pypoetry/cache poetry install --only main --no-interaction --no-ansi

FROM python_dependencies_pbsv2 as collectstatic_pbsv2

COPY --chown=oim:oim gunicorn.conf.py manage.py manage.sh ./
COPY --chown=oim:oim govapp ./govapp
COPY --chown=oim:oim .git ./.git

RUN touch /app/.env && \
    poetry run python manage.py collectstatic --no-input

FROM collectstatic_pbsv2 as build_vue_pbsv2

RUN cd /app/govapp/frontend/pbs ; npm ci --omit=dev && \
    cd /app/govapp/frontend/pbs ; npm run build

FROM build_vue_pbsv2 as launch_pbsv2

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
