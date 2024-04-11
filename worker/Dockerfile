FROM python:3.11

ARG MODEL_VERSION=2.4

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false\
    MODEL_VERSION=${MODEL_VERSION}

ENV POETRY_HOME=/opt/poetry\
    PATH="${PATH}:/opt/poetry/bin"
RUN python3 -m venv ${POETRY_HOME} &&\
    ${POETRY_HOME}/bin/pip install poetry==${POETRY_VERSION} &&\
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    alsa-utils \
    ffmpeg && \
    apt-get clean

RUN curl -L -o model.tflite "https://raw.githubusercontent.com/kahst/BirdNET-Analyzer/main/checkpoints/V${MODEL_VERSION}/BirdNET_GLOBAL_6K_V${MODEL_VERSION}_Model_FP32.tflite"
RUN curl -L -o labels.txt "https://raw.githubusercontent.com/kahst/BirdNET-Analyzer/main/labels/V${MODEL_VERSION}/BirdNET_GLOBAL_6K_V${MODEL_VERSION}_Labels_de.txt"

COPY analyzer.py recorder.py ./
