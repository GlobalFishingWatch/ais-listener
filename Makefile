VENV_NAME:=.venv
REQS_PROD:=requirements.txt
REQS_DEV:=requirements/dev.txt
DOCKER_DEV_SERVICE:=dev

GCP_PROJECT:=world-fishing-827
GCP_DOCKER_VOLUME:=gcp

## help: Prints this list of commands.
## gcp: Authenticates to google cloud and configure the project.
## build: Builds docker image.
## dockershell: Enters to docker container shell.
## reqs: Compiles requirements.txt file with pip-tools.
## upgrade-reqs: Upgrades requirements.txt.
## venv: Creates a virtual environment.
## install: Installs all dependencies needed for development.
## test: Runs unit tests.
## testdocker: Runs unit and integration tests inside docker container.
## ci-test: Runs tests for the CI exporting coverage.xml report.

help:
	@echo "\nUsage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/-/'

volume:
	docker volume create --name ${GCP_DOCKER_VOLUME}

gcp:
	make volume
	docker compose run gcloud auth application-default login
	docker compose run gcloud config set project ${GCP_PROJECT}
	docker compose run gcloud auth application-default set-quota-project ${GCP_PROJECT}

build:
	docker compose build

dockershell:
	docker compose run --rm -it ${DOCKER_DEV_SERVICE}

reqs:
	docker compose run --rm ${DOCKER_DEV_SERVICE} -c \
		'pip-compile -o ${REQS_PROD} -v'

upgrade-reqs:
	docker compose run --rm ${DOCKER_DEV_SERVICE} -c \
		'pip-compile -o ${REQS_PROD} -U -v'

venv:
	python -m venv ${VENV_NAME}

install:
	pip install -r ${REQS_DEV}
	pip install -e .

test:
	pytest

testdocker: volume
	docker compose run --rm ${DOCKER_DEV_SERVICE}

ci-test: volume
	docker compose run --rm --entrypoint pytest ${DOCKER_DEV_SERVICE} --cov-report=xml


.PHONY: help volume gcp build dockershell reqs upgrade-reqs venv install test testdocker ci-test
