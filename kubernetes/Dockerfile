FROM python:3.10.14-slim

WORKDIR /app

COPY code/.settings/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt \
    && rm -rf ~/.cache/pip