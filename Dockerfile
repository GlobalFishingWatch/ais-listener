FROM python:3.12-alpine AS base

RUN apk update && apk add build-base

# Configure the working directory
RUN mkdir -p /opt/project
WORKDIR /opt/project

# Setup a volume for configuration and auth data
VOLUME ["/root/.config"]

# Install application dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10110/udp

ENTRYPOINT [ "socket-listener"]

# ---------------------------------------------------------------------------------------
# PROD
# ---------------------------------------------------------------------------------------
FROM base AS prod

# Install app package
COPY . /opt/project
RUN pip install . && \
    rm -rf /root/.cache/pip && \
    rm -rf /opt/project/*

# ---------------------------------------------------------------------------------------
# DEV
# ---------------------------------------------------------------------------------------
FROM base AS dev

COPY ./requirements/dev.txt .
COPY ./requirements/test.txt .

RUN pip install --no-cache-dir -r dev.txt
RUN pip install --no-cache-dir -r test.txt

# Install app package
COPY . /opt/project
RUN pip install -e .

# ---------------------------------------------------------------------------------------
# TEST IMAGE (This checks that package is properly installed in prod image)
# ---------------------------------------------------------------------------------------
FROM prod AS test

COPY ./config /opt/project/config
COPY ./sample /opt/project/sample

COPY ./tests /opt/project/tests
COPY ./requirements/test.txt /opt/project/

RUN pip install -r test.txt
