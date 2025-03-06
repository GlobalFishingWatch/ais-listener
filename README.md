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
We have generalized this functionality for any desired data sources and destinations.

The service can run in different modes,
depending on the network protocol used
and the implementation (server-like or client-like).
In every case we call these objects **_receivers_** or **_listeners_**.

Currently, the following receivers/listeners are supported:
- UDPSocketReceiver: UDP server that listens on a socket and accepts clients requests asynchronously.
- ClientTCPSocketReceiver: TCP client that connects to a socket server and continuously requests new data.

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
(.venv) $ socket-listener receiver -h
usage: Socket Listener (v0.1.0). receiver [-h] [-v] [-c  ] [--no-rich-logging] [--project  ] [--protocol  ] [--host  ] [--port  ] [--max-packet-size  ] [--max-retries  ]
                                          [--init-retry-delay  ]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Set logger level to DEBUG.
  -c, --config-file     Path to config file. If passed, rest of CLI args are ignored (default: None).
  --no-rich-logging     Disable rich logging [useful for production environments].
  --project             GCP project id (default: world-fishing-827).
  --protocol            Network protocol to use. One of [UDP, TCP] (default: UDP).
  --host                IP to use (as server) or to connect to (as client) (default: localhost).
  --port                Port to use (as server) or to connect to (as client) (default: 10110).
  --max-packet-size     Max. size in bytes for the internal buffer [for clients] (default: 4096).
  --max-retries         Max. retries if a connection fails [for clients] (default: inf).
  --init-retry-delay    Initial retry delay when a connection fails [for clients] (default: 1).
```

Examples:
```shell
socket-listener receiver --protocol TCP_client --host 153.44.253.27 --port 5631
```

```shell
socket-listener receiver --protocol UDP
```

```shell
socket-listener receiver -c config/TCP-client-kystverket.yaml
```

Example of configuration file:
```yaml
source_name: 'kystverket'
protocol: TCP_client
host: 153.44.253.27
port: 5631
max_packet_size: 4096
max_retries: .inf
max_retry_delay: 60
init_retry_delay: 1
```

#### Running within docker

To run in docker:
```shell
docker compose run --rm receiver --protocol TCP_client --host 153.44.253.27 --port 5631
```

```shell
docker compose run --rm receiver -c config/TCP-client-kystverket.yaml
```

## Development

A pair of _**transmitters**_ are provided that can be used for testing.

To send test messages via UDP (client-like) use
```shell
socket-listener transmitter --protocol=UDP --port [PORT_TO_LISTEN]
```

To send messages via TCP (server-like), use
```shell
socket-listener transmitter --protocol=TCP --port [PORT_TO_CONNECT]
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
make upgrade-reqs
```

### Docker utils

For convenience, there are some shell scripts for building and running using `docker compose`:
+ `build.sh`: This will run `docker compose build` and pass in some extra info on the current git commit.
+ `cloud-build.sh`: This will do a manual cloud build and publish the docker container to the cloud registry.

### Build and Deploy

This tool is designed to be run in a GCE instance as a docker image.   

Pushing a commit to the main branch will automatically trigger a cloud build. 
You can use `cloud-build.sh` to manually trigger a build. 

Then you have to deploy the docker container in a GCP instance,
configure command line parameters,
assign an external IP, 
and open the UDP ports in the firewall.  

You can use the client app to test.