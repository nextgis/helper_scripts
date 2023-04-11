FROM ubuntu:focal

ARG DEBIAN_FRONTEND=noninteractive

# Install GDAL by NextGIS with latest SXF driver

RUN apt-get update -y && \
	apt-get -y install --no-install-recommends --yes language-pack-ru \
	apt-transport-https ca-certificates curl gnupg && \
	echo "deb https://rm.nextgis.com/api/repo/11/deb focal main" | tee -a /etc/apt/sources.list && \
	curl -s -L https://rm.nextgis.com/api/repo/11/deb/key.gpg | apt-key add - && \
	apt-get update -y && \
	apt-get -y install --no-install-recommends --yes python3 python3-pip gdal-bin python3-gdal python3-setuptools && \
	update-locale LANG=ru_RU.UTF-8 && \
	pip3 install --upgrade pip

RUN apt-get install --yes git
RUN pip3 install --upgrade --force-reinstall git+https://github.com/nextgis/pyngw.git

# copying of script into image while build

RUN mkdir /opt/changeowners
COPY . /opt/changeowners
WORKDIR /opt/changeowners


ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8
