<h1 align="center" style="border-bottom: none;"> AIS Listener </h1>

<p align="center">
  <a href="https://codecov.io/gh/GlobalFishingWatch/ais-listener" > 
    <img src="https://codecov.io/gh/GlobalFishingWatch/ais-listener/graph/badge.svg?token=VrsRdRuei9"/> 
  </a>
  <a>
    <img alt="Python versions" src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue">
  </a>
  <a>
    <img alt="Docker Engine version" src="https://img.shields.io/badge/DockerEngine-v27-yellow">
  </a>
  <a>
    <img alt="Last release" src="https://img.shields.io/github/v/release/GlobalFishingWatch/ais-listener">
  </a>
</p>

A service that receives NMEA-encoded AIS messages via UDP or TCP and writes them to GCS.

[requirements.txt]: requirements.txt
[pyproject.toml]: pyproject.toml
[sample/sources.yaml]: sample/sources.yaml
[sample/nmea.txt]: sample/nmea.txt

## Introduction

<div align="justify">

This is a dockerized micro service that provides UDP and TCP services. The UDP service will listen on multiple ports 
for NMEA messages data streams. The TCP service will connect to a designated host and then read messages.
A tagblock is added or updated to include a timestamp, source and station, and the resulting 
messages are written in the order received to a sharded and gzipped GCS file.

</div>

## Usage

### Installation

We still don't have a package in PYPI.

First, clone the repository.

Create virtual environment and activate it:
```shell
python -m venv .venv
./.venv/bin/activate
```
Install dependencies and the python package:
```shell
make install
```
Make sure you can run unit tests:
```shell
make test
```
Make sure you can build the docker image:
```shell
make build
```
In order to be able to connect to BigQuery, authenticate and configure the project:
```shell
make gcp
```

### Using the CLI

```shell
(.venv) $ ais-listener receiver -h
usage: AIS Listener (v0.1.0). receiver [-h] [--buffer-size ] [--gcs-dir ] [--config_file ] [--shard-interval ]

options:
  -h, --help          show this help message and exit
  --buffer-size       Size in bytes for the internal buffer (default: 4096).
  --gcs-dir           GCS directory to write nmea shard files (default: gs://scratch-paul-ttl100/ais-listener/).
  --config_file       File to read to get mapping of listening ports to source names (default: sample/sources.yaml).
  --shard-interval    Maximum interval in seconds between the first line and last line written to a single shard file (default: 300).
```

Example:
```shell
ais-listener -v receiver \
   --gcs-dir gs://my_bucket/some_dir/ \
   --config_file gs://my_bucket/source-port-map.yaml
```

The service will receive files for each source in sources.
For UDP, the service will listen on the designated port,
and for TCP the service will connect to the designated host and port.

Output files are written in the given GCS directory in a sub directory by date.
Files are sharded every 5 minutes by default, and the file name is formatted

`[GCS_DIR/[YYYYMMDD]/][source]_[YYYYMMDD]_[HHMMSS]_[uuid].nmea.gz`.

The source is the source label from `sources.yaml`.

There is also a par of transmitters that can be used for testing.  

To send test messages via UDP use
```shell
ais-listener -v transmitter \
  --protocol=UDP \
  --port=[PORT_TO_LISTEN] 
```

To send messages via TCP, use
```shell
ais-listener -v transmitter \
  --protocol=TCP \
  --port [PORT_TO_CONNECT]
```

Running this will read values from [sample/nmea.txt] by default.

You can run the receiver and the transmitter locally and the transmitter should send messages to the receiver.   
Use `-v` for verbose output and both transmitter and receiver should print every message to the console.


### Running within docker

To run in docker, displaying the server's command line parameters 
```shell
docker compose run --rm server --help
```

## Updating dependencies

The [requirements.txt] contains all transitive dependencies pinned to specific versions.
This file is compiled automatically with [pip-tools], based on [pyproject.toml].

Use [pyproject.toml] to specify high-level dependencies with some restrictions.
Do not modify [requirements.txt] manually.

To re-compile dependencies, just run
```shell
make reqs
```

If you want to upgrade all dependencies to latest available versions
(compatible with restrictions declared), just run:
```shell
make upgrade-reqs
```

### Docker utils

For convenience, there are some shell scripts for building and running using `docker compose`:
+ `build.sh`: This will run `docker compose build` and pass in some extra info on the current git commit.
+ `cloud-build.sh`: This will do a manual cloud build and publish the docker container to the cloud registry.

## Build and Deploy

This tool is designed to be run in a GCE instance as a docker image.   

Pushing a commit to the main branch will automatically trigger a cloud build. 
You can use `cloud-build.sh` to manually trigger a build. 

Then you have to deploy the docker container in a GCP instance,
configure command line parameters,
assign an external IP, 
and open the UDP ports in the firewall.  

You can use the client app to test.