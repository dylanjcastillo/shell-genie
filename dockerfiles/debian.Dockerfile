# syntax=docker/dockerfile:1

FROM python:3.11.1-slim

WORKDIR /app

COPY . .

ENV POETRY_VERSION=1.3.2
ENV POETRY_VENV=/opt/poetry/venv
ENV SHELL=/bin/bash

RUN python3 -m venv $POETRY_VENV && $POETRY_VENV/bin/pip install -U pip setuptools && $POETRY_VENV/bin/pip install poetry

ENV PATH="${PATH}:${POETRY_VENV}/bin"

RUN poetry check
RUN poetry config virtualenvs.create false
RUN poetry install
