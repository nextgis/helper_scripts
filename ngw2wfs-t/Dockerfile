# FROM python:3-bullseye
FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get -y install --no-install-recommends --yes \
    ca-certificates curl gdal-bin python3-gdal python3-requests bash 

COPY . /app