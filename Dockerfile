FROM gcr.io/world-fishing-827/github.com/globalfishingwatch/gfw-pipeline:latest-python3.9
LABEL maintainer="paul@globalfishingwatch.org"

ARG COMMIT="unknown"
ARG REPO="unknown"
ARG BRANCH="unknown"

LABEL commit_sha=${COMMIT}
LABEL commit_branch=${BRANCH}
LABEL commit_repo=${REPO}

ENV COMMIT_SHA=${COMMIT}
ENV COMMIT_BRANCH=${BRANCH}
ENV COMMIT_REPO=${REPO}

WORKDIR /opt/code

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE 10110/udp

ENTRYPOINT [ "python", "-u", "main.py"]
