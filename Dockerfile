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

ENTRYPOINT [ "ais-listener"]

# ---------------------------------------------------------------------------------------
# PROD
# ---------------------------------------------------------------------------------------
FROM base AS prod

# Install app package
COPY . /opt/project
RUN pip install .

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

