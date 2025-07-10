# ---------------------------------------------------------------------------------------
# BASE IMAGE
# ---------------------------------------------------------------------------------------
FROM python:3.12.10-slim-bookworm AS base

# Setup a volume for configuration and authtentication.
VOLUME ["/root/.config"]

# Update system and install build tools. Remove unneeded stuff afterwards.
# Upgrade PIP.
# Create working directory.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    mkdir -p /opt/project

# Set working directory.
WORKDIR /opt/project

EXPOSE 10110/udp

ENTRYPOINT ["socket-listener"]

# ---------------------------------------------------------------------------------------
# DEPENDENCIES IMAGE (installed project dependencies)
# ---------------------------------------------------------------------------------------
# We do this first so when we modify code while development, this layer is reused
# from cache and only the layer installing the package executes again.
FROM base AS deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------------------------------------------------------------------------------------
# PRODUCTION IMAGE
# ---------------------------------------------------------------------------------------
FROM deps AS prod

COPY . /opt/project
RUN pip install . && \
    rm -rf /root/.cache/pip && \
    rm -rf /opt/project/*


# ---------------------------------------------------------------------------------------
# DEVELOPMENT IMAGE (editable install and development tools)
# ---------------------------------------------------------------------------------------
FROM deps AS dev

COPY . /opt/project
RUN pip install -e .[lint,dev,build]

# ---------------------------------------------------------------------------------------
# TEST IMAGE (This checks that package is properly installed in prod image)
# ---------------------------------------------------------------------------------------
FROM prod AS test

COPY ./requirements-test.txt /opt/project/
RUN pip install -r requirements-test.txt

COPY ./tests /opt/project/tests
COPY ./config /opt/project/config