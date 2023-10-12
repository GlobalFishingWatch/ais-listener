# AIS Listener

A UDP listener that receives NMEA-encoded AIS messages via UDP and writes them to GCS

## Introduction

This is a dockerized micro service that provides a UDP server which will listen on a range of UDP ports for NMEA
data streams.  A tagblock is added or updated to include a timestamp, source and station, and the resulting 
messages are written in the order received to a sharded and gzipped GCS file

To run the server and listen on localhost to udp ports 10110, 10111, 10112

```console
python main.py -v server \
   --udp-port-range 10110 10112 \
   --gcs-dir gs://my_bucket/some_dir/ \
   --source-port-map gs://my_bucket/source-port-map.yaml
```

The server will listen to all the UDP ports in the range.  To listen on just one port, use the same value for 
start and end.

Output files will be written in the given GCS directory in a sub directory by date.  Files are sharded every 5 minutes by default, and the 
file name is formatted

`[GCS_DIR/[YYYYMMDD]/][source]_[YYYYMMDD]_[HHMMSS]_[uuid].nmea.gz`

The source is the source label from `source-port-map` that is mapped to the UDP port that receives the message 

An example source-port-map file is in sample/sources.yaml

There is also a client that can be used for testing.  All it does is read messages from a file and send them to a 
designated UDP port.

Running this in the project folder will read values from `sample/nmea.txt` and send to `localhost:10110`

```console
python main.py -v client
```

You can run the server and the client locally and the client should send messages to the server.   Use `-v` for 
verbose output and both client and server should print every message to the console.

## Developing 
To set up the development environment
```commandline
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Repository structure

The following are important files and folders in the repository:

* `requirements.txt`: Like for any standard python package, this file contains any python dependencies you need installed in your docker container for your pipeline to work. These dependencies are automatically installed when you run `docker-compose build`.
* `main.py`: This is the application entry point.   This mostly just deals with parsing command line parameters and then passing control off to pipeline.py
* `pipeline.py`: This is where the work is done. See the example pipeline code as a guide for how to structure this
* `util/`: This folder contains some utility modules.

## Unit tests
There are a few unit tests, but most of the code is not covered.   Run the tests with 

```console
pytest tests
```

## Build and Deploy
This tool is designed to be run in a GCE instance as a docker image.   

### Docker setup

We use a dockerized development environment, so you will need [docker](https://www.docker.com/)  and [docker-compose](https://docs.docker.com/compose/) on your machine . We also need the [google cloud sdk](https://cloud.google.com/sdk/) installed locally to generate the authorization files that will be used to authorize access to google cloud services. No other dependencies are required in your machine.

To setup google cloud sdk authorization, follow these steps:

* Make sure to have a working google cloud sdk installation, and that you've logged in.

* Configure docker to use google cloud to authorize access to our base images by running `gcloud auth configure-docker`.

* Create a docker volume named `gcp` to store the google cloud credentials that docker will use by running `docker volume create --name gcp`. This volume will be shared by all your pipeline repositories, so you need to run this only once.

* Setup GCP authorization inside docker by running `docker-compose run --rm gcloud --project=world-fishing-827 auth application-default login` and following the instructions.

For convenience, there are some shell scripts for building and running using `docker compose`
+ `build.sh`    This will run `docker compose build` and pass in some extra info on the current git commit
+ `cloud-build.sh` This will do a manual cloud build and publish the docker container to the cloud registry


### Running within docker
To run in docker, displaying the server's command line parameters 
```console
docker compose run --rm server --help
```
Note that the first time you do this, docker will build the image for you. This will take a minute...

### Deploy
Pushing a commit to the main branch will automatically trigger a cloud build.  You can use `cloud-build.sh` 
to manually trigger a build. 

Deploy the docker container in a GCP instance, configure command line parameters, assign an external IP, 
and open the UDP ports in the firewall.  

Use the client app to test
