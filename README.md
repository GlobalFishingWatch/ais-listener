<h1 align="center" style="border-bottom: none;"> socket-listener </h1>

<p align="center">
  <a href="https://codecov.io/gh/GlobalFishingWatch/ais-listener" > 
    <img src="https://codecov.io/gh/GlobalFishingWatch/ais-listener/branch/dev/graph/badge.svg?token=VrsRdRuei9"/> 
  </a>
  <a>
    <img alt="Python versions" src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue">
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

[PubSub sink]: socket_listener/sinks/pubsub.py

## Introduction

<div align="justify">

The original motivation for this service was to support
the ingestion of AIS messages required by GFW data pipelines.
Since then, we have generalized the functionality to support arbitrary network protocols, data sources, and destinations.
We intentionally keep the server **thin and focused solely on ingestion**,
without performing any parsing or transformation of the input data.
All decoding and processing is deferred to downstream pipelines,
allowing for greater flexibility and scalability.

</div>

> [!NOTE]
> **Currently supported options:**
>
> - 📡 **Protocols**: `UDP`.
> - 🎯 **Destinations**: `PubSub`.

## PubSub

The [PubSub sink] supports two modes, controlled by the `pubsub-data-format` parameter:

- **`raw`**: The entire socket packet is published as-is in a single **PubSub** message.
- **`split`**: The socket packet is split using a configurable `delimiter`,
  and each component is published as a separate **PubSub** message.


## Usage

### Installation

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
make install-all
```
Make sure you can run unit tests:
```shell
make test
```

### Using the CLI

```shell
(.venv) $ socket-listener receiver -h
usage: socket-listener (v0.1.0). (v0.1.0). receiver [-h] [-c] [-v] [--log-file] [--no-rich-logging] [--only-render] [--protocol] [--host] [--port] [--daemon-thread] [--max-packet-size]
                                                    [--delimiter] [--ip-client-mapping-file] [--thread-monitor-delay] [--pubsub] [--pubsub-project] [--pubsub-topic] [--pubsub-data-format]

options:
  -h, --help                 show this help message and exit

built-in CLI options:
  -c , --config-file         Path to config file. (default: None)
  -v, --verbose              Set logger level to DEBUG. (default: False)
  --log-file                 File to send logging output to. (default: None)
  --no-rich-logging          Disable rich logging [useful for production environments]. (default: False)
  --only-render              Dry run, only renders command line call and prints it. (default: False)

options defined by 'socket-listener (v0.1.0).' command:
  --protocol                 Network protocol to use. (default: UDP)
  --host                     IP to use. (default: 0.0.0.0)
  --port                     Port to use. (default: 10110)
  --daemon-thread            Run main process in a daemonic thread [Useful for testing]. (default: False)

options defined by 'receiver' command:
  --max-packet-size          The maximum amount of data to be received at once. (default: 4096)
  --delimiter                Delimiter to use when splitting incoming packets into messages. (default: None)
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

Example of configuration file for the receiver command:
```yaml
protocol: UDP
port: 10110
max_packet_size: 4096
daemon_thread: False
delimiter: "\n"
pubsub: True
pubsub_project: "world-fishing-827"
pubsub_topic: "nmea-stream-scratch"
pubsub_data_format: "raw"
```

#### Running within docker

To run in docker with development docker image:
```shell
docker compose run --rm dev receiver -c config/UDP-pubsub-nmea-stream-scratch.yaml
```

## Development

A socket _**transmitter**_ object exists that can be used for testing.

For example:
```shell
socket-listener transmitter -p PATH_TO_FILE_OR_DIR --chunk-size 600 --delay 0.5
```

### Updating dependencies

<div align="justify">

The [requirements.txt] file contains all transitive dependencies pinned to specific versions.
It is automatically generated using [pip-tools],
based on the dependencies specified in [pyproject.toml].
This process ensures reproducibility,
allowing the application to run consistently across different environments.

Use [pyproject.toml] to define high-level dependencies with flexible version constraints
(e.g., ~=1.2, >=1.0, <2.0, ...).

To re-compile dependencies, just run
```shell
make reqs
```

If you want to upgrade all dependencies to latest compatible versions, just run:
```shell
make reqs-upgrade
```
</div>

> [!IMPORTANT]
> Do not modify [requirements.txt] manually.

> [!NOTE]
> Remember that if you change the [requirements.txt],
you need to rebuild the docker image (`make docker-build`) in order to use it locally.

### How to deploy

A Google Cloud build that publishes a Docker image is triggered in the following cases:  
- When a commit is merged into `main`.  
- When a new tag is created.
