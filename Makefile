VENV_NAME:=.venv
REQS_PROD:=requirements.txt
REQS_DEV:=requirements/dev.txt

DOCKER_SHELL_SERVICE:=shell
DOCKER_DEV_SERVICE:=dev
DOCKER_TEST_SERVICE:=test

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

.PHONY: help
help:
	@echo "\nUsage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/-/'

.PHONY: docker-volume
docker-volume:
	docker volume create --name ${GCP_DOCKER_VOLUME}

.PHONY: docker-gcp
docker-gcp:
	make docker-volume
	docker compose run gcloud auth application-default login
	docker compose run gcloud config set project ${GCP_PROJECT}
	docker compose run gcloud auth application-default set-quota-project ${GCP_PROJECT}

.PHONY: docker-build
docker-build:
	docker compose build

.PHONY: docker-shell
docker-shell:
	docker compose run --rm -it ${DOCKER_SHELL_SERVICE}

.PHONY: docker-test
docker-test: docker-volume
	docker compose run --rm ${DOCKER_DEV_SERVICE}

.PHONY: docker-ci-test
docker-ci-test: docker-volume
	docker compose run --rm ${DOCKER_TEST_SERVICE}

.PHONY: reqs
reqs:
	docker compose run --rm ${DOCKER_DEV_SERVICE} -c \
		'pip-compile -o ${REQS_PROD} -v'

.PHONY: reqs-upgrade
reqs-upgrade:
	docker compose run --rm ${DOCKER_DEV_SERVICE} -c \
		'pip-compile -o ${REQS_PROD} -U -v'

.PHONY: venv
venv:
	python -m venv ${VENV_NAME}

.PHONY: install
install:
	pip install -r ${REQS_DEV}
	pip install -e .

.PHONY: test
test:
	python -m pytest --cov-report term --cov-report=xml


