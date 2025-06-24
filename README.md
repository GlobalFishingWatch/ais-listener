<h1 align="center" style="border-bottom: none;"> Socket Listener </h1>

<p align="center">
  <a href="https://codecov.io/gh/GlobalFishingWatch/ais-listener" > 
    <img src="https://codecov.io/gh/GlobalFishingWatch/ais-listener/branch/dev/graph/badge.svg?token=VrsRdRuei9"/> 
  </a>
  <a>
    <img alt="Python versions" src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue">
  </a>
  <a>
    <img alt="Docker Engine version" src="https://img.shields.io/badge/DockerEngine-v27-yellow">
  </a>
  <a>
    <img alt="Last release" src="https://img.shields.io/github/v/release/GlobalFishingWatch/ais-listener">
  </a>
</p>

A service that receives messages through network sockets and publish them to desired destinations.

[pip-tools]: https://pip-tools.readthedocs.io/en/stable/
[pyproject.toml]: pyproject.toml
[requirements.txt]: requirements.txt
[sample/sources.yaml]: sample/sources.yaml
[sample/nmea.txt]: sample/nmea.txt

## Introduction

<div align="justify">

The original motivation for this service
was the ingestion of AIS messages needed by GFW data pipelines.
We have generalized this functionality for any desired network protocols,
data sources and destinations.

</div>

> [!NOTE]
> Currently, only **UDP** protocol is supported.

## Usage

### Installation

We still don't have a package in PYPI.

First, clone the repository.

Make sure you can build the docker image:
```shell
make docker-build
```
In order to be able to connect to BigQuery, authenticate and configure the project:
```shell
make docker-gcp
```
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

### Using the CLI

```shell
(.venv) $ socket-listener receiver -h
usage: Socket Listener (v0.1.0). (v0.1.0). receiver [-h] [-c] [-v] [--log-file] [--no-rich-logging] [--only-render] [--protocol] [--host] [--port] [--daemon-thread] [--max-packet-size]
                                                    [--delimiter] [--ip-client-mapping-file] [--thread-monitor-delay] [--pubsub] [--pubsub-project] [--pubsub-topic] [--pubsub-data-format]

options:
  -h, --help                 show this help message and exit

built-in CLI options:
  -c , --config-file         Path to config file. (default: None)
  -v, --verbose              Set logger level to DEBUG. (default: False)
  --log-file                 File to send logging output to. (default: None)
  --no-rich-logging          Disable rich logging [useful for production environments]. (default: False)
  --only-render              Dry run, only renders command line call and prints it. (default: False)

options defined by 'Socket Listener (v0.1.0).' command:
  --protocol                 Network protocol to use. (default: UDP)
  --host                     IP to use. (default: 0.0.0.0)
  --port                     Port to use. (default: 10110)
  --daemon-thread            Run main process in a daemonic thread [Useful for testing]. (default: False)

options defined by 'receiver' command:
  --max-packet-size          The maximum amount of data to be received at once. (default: 4096)
  --delimiter                Delimiter to use when splitting incoming packets into messages. (default: 
                             )
  --ip-client-mapping-file   Path to (IP -> client_name) mappings. (default: None)
  --thread-monitor-delay     Number of seconds between each log entry of ThreadMonitor. (default: None)
  --pubsub                   Enable publication to Google PubSub service. (default: False)
  --pubsub-project           GCP project id. (default: world-fishing-827)
  --pubsub-topic             Google Pub/Sub topic id. (default: nmea-stream-dev)
  --pubsub-data-format       Data format to use for Google Pub/Sub messages. (default: raw)
```

Examples:
```shell
socket-listener receiver --protocol UDP --port 10112 --max-packet-size 4096
```

Example of configuration file:
```yaml
protocol: UDP
port: 10110
max_packet_size: 65536
daemon_thread: False
delimiter: "\n"
pubsub: True
pubsub_project: "world-fishing-827"
pubsub_topic: "nmea-stream-scratch"
pubsub_data_format: "raw"
```

#### Running within docker

To run in docker:
```shell
docker compose run --rm dev -c config/UDP-pubsub-nmea-stream-dev.yaml
```

## Development

A socket _**transmitter**_ object exists that can be used for testing.

For example:
```shell
socket-listener transmitter -p PATH_TO_FILE_OR_DIR --chunk-size 600 --delay 0.5
```

### Updating dependencies

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
make reqs-upgrade
```

### How to deploy

Pushing a commit to the master or dev branches
will automatically trigger a Google Cloud build and the docker image will be published.
