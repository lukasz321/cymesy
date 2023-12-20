FROM python:3.9.13-slim

ARG POETRY_HTTP_BASIC_DENSITY_USERNAME
ARG POETRY_HTTP_BASIC_DENSITY_PASSWORD

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt update && apt-get install -y build-essential
RUN mkdir /app

# Install Poetry & ensure it is in $PATH
RUN pip install "poetry==${POETRY_VERSION}"
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/root/.poetry/bin:${VIRTUAL_ENV}/bin:${PATH}"

# Initialize virtual env...
RUN python3 -m venv $VIRTUAL_ENV

# copy only requirements to cache them in separate layer
WORKDIR /app
COPY README.md poetry.lock pyproject.toml /app/
COPY ./src /app/src

# Update pip
RUN python -m pip install -U pip

# project initialization
RUN poetry install --no-dev --no-interaction

# run dockerfile
CMD ["sh", "-c", "python3 -m src.static_noise $SENSOR_SERIAL_NUMBER --sqs_url $AMAZON_SQS_URL" ]
