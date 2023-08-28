FROM python:3.10-alpine3.13
LABEL maintainer="paccuk"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./requirements.dev.txt /tmp/
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false

RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql && \
    apk add --update --no-cache --virtual .build-deps \
        build-base postgresql-dev musl-dev linux-headers && \
    /venv/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; then \
        /venv/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .build-deps && \
    adduser  \
        --disabled-password \
        --no-create-home \
        django-user && \
    chmod -R +x /scripts


ENV PATH="/scripts:/venv/bin:$PATH"

USER django-user

CMD ["run.sh"]