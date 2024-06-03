FROM gcr.io/world-fishing-827/github.com/globalfishingwatch/gfw-pipeline:latest-python3.11-alpine
LABEL maintainer="paul@globalfishingwatch.org"

ARG COMMIT="unknown"
ARG REPO="unknown"
ARG BRANCH="unknown"
ARG TAG="unknown"

LABEL commit_sha=${COMMIT}
LABEL commit_branch=${BRANCH}
LABEL commit_repo=${REPO}
LABEL commit_tag=${TAG}

ENV COMMIT_SHA=${COMMIT}
ENV COMMIT_BRANCH=${BRANCH}
ENV COMMIT_REPO=${REPO}
ENV COMMIT_TAG=${TAG}

WORKDIR /opt/code

RUN apk update && apk add build-base

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 10110/udp

ENTRYPOINT [ "python", "-u", "main.py"]
