# AIS Listenere

## Introduction

A UDP listener that receives NMEA-encoded AIS messages via UDP and publishes them to pubsub

## Prerequisites

We use a dockerized development environment, so you will need [docker](https://www.docker.com/)  and [docker-compose](https://docs.docker.com/compose/) on your machine . We also need the [google cloud sdk](https://cloud.google.com/sdk/) installed locally to generate the authorization files that will be used to authorize access to google cloud services. No other dependencies are required in your machine.

To setup google cloud sdk authorization, follow these steps:

* Make sure to have a working google cloud sdk installation, and that you've logged in.

* Configure docker to use google cloud to authorize access to our base images by running `gcloud auth configure-docker`.

* Create a docker volume named `gcp` to store the google cloud credentials that docker will use by running `docker volume create --name gcp`. This volume will be shared by all your pipeline repositories, so you need to run this only once.

* Setup GCP authorization inside docker by running `docker-compose run --rm gcloud --project=world-fishing-827 auth application-default login` and following the instructions.

## Repository structure
[TODO: Update this as needed]

The following are important files and folders in the repository:

* `requirements.txt`: Like for any standard python package, this file contains any python dependencies you need installed in your docker container for your pipeline to work. These dependencies are automatically installed when you run `docker-compose build`.
* `main.py`: This is the application entry point.   This mostly just deals with parsing command line parameters and then passing control off to pipeline.py
* `pipeline.py`: This is where the work is done. See the example pipeline code as a guide for how to structure this
* `util/`: This folder contains some utility modules. 
* `assets/`: This folder contains data files such as jinja2 templated sql queries and json-formatted bigquery schema files 

## Running locally
[TODO: Replace this as needed]
This template comes with a fully functional example pipeline which should run for you if everything is configured correctly.

You can run the pipeline from within docker (which is how it will run when automated), or you can run it locally on your machine

### Running within docker
To run in docker, displaying the pipeline's command line parameters 
```console
docker compose run --rm pipeline --help
```
Note that the first time you do this, docker will build the image for you. This will take a minute...

To run the pipeline in test mode with default parameters
```console
docker compose run --rm pipeline --test fishing_hours
```

To run it for real, you can do something like
```console
docker compose run --rm pipeline \
 --dest_fishing_hours_flag_table=world-fishing-827.scratch_public_ttl120.example_fishing_hours_by_flag \
 fishing_hours
```

For more complete examples, see `run.sh`

### Running from your local python environment

You can also run and test using your local python environment.   This can sometimes make debugging faster and easier, but remember that when this gets run in the cloud, it will be running inside the docker container, so that also needs to work.

To setup your local python environment
```console
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then to run the pipeline
```console
python main.py --help
```

For convenience, there are some shell scripts for building and running using `docker compose`
+ `build.sh`    This will run `docker compose build` and pass in some extra info on the current git commit
+ `run.sh`      This will run the pipeline using `docker compose run`.  Edit the file to set the parameters you want to use
+ `cloud-build.sh` This will do a manual cloud build and publish the docker container to the cloud registry


