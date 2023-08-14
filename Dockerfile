FROM python:3.10-alpine3.13
LABEL maintainer="paccuk"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./requirements.dev.txt /tmp/
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false

RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; then \
        /venv/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser  \
        --disabled-password \
        --no-create-home \
        django-user


ENV PATH="/venv/bin:$PATH"

USER django-user