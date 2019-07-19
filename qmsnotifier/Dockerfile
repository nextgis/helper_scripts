FROM python:3-slim-stretch

# This will make apt-get install without question
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && apt-get install --no-install-recommends -y cron bash && apt-get clean -y && apt-get autoclean -y  && rm -rf /var/cache/* /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install --upgrade pip setuptools && \
    pip3 install beautifulsoup4 requests pysocks && \
    mkdir /home/qmsnotifier/ && \
    mkdir /home/qmsnotifier/data

COPY crontab /etc/crontab

COPY qmsnotifier3.py /home/qmsnotifier/qmsnotifier3.py
COPY tele /home/qmsnotifier/tele
COPY token /home/qmsnotifier/token
COPY qms.json /home/qmsnotifier/qms.json

COPY run.sh /home/qmsnotifier/run.sh
RUN chmod +x /home/qmsnotifier/run.sh
COPY run-init.sh /home/qmsnotifier/run-init.sh
RUN chmod +x /home/qmsnotifier/run-init.sh

CMD ["/home/qmsnotifier/run-init.sh"]
