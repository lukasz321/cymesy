PYPI_PASSWORD ?= $(shell cat ~/.directory/pypi || $$PYPI_PASSWORD)

account     := 937369328181
image       := density/$(shell basename `git rev-parse --show-toplevel`)
tag         ?= $(shell git rev-parse --short=7 HEAD)
region      := us-east-1

docker.build:
	docker build . \
		-t $(image):0 \
		--build-arg POETRY_HTTP_BASIC_ORG_USERNAME=density \
		--build-arg POETRY_HTTP_BASIC_ORG_PASSWORD=$(PYPI_PASSWORD) \
		--build-arg GIT_HASH=$(tag)

docker.run:
	docker run \
        -e SENSOR_SERIAL_NUMBER=$(SENSOR_SERIAL_NUMBER) \
		-e AMAZON_SQS_URL=$(AMAZON_SQS_URL) \
		-e AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
		-e AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
		docker.io/$(image):0

deploy.lab:
	AWS_REGION=us-east-1 chute plan lab-us-east-1 floorplan-processor.hcl

deploy.production:
	AWS_REGION=us-east-1 chute plan production-us-east-1 floorplan-processor.hcl
