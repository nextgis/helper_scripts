FROM python:3-alpine

RUN pip3 install --upgrade pip setuptools && \
    pip3 install beautifulsoup4 requests pysocks && \
    mkdir /home/qmsmonitor

COPY qmsnotifier3.py /home/qmsmonitor/qmsnotifier3.py
COPY tele /home/qmsmonitor/tele
COPY token /home/qmsmonitor/token
COPY qms.json /home/qmsmonitor/qms.json

WORKDIR /home/qmsmonitor
CMD ["python", "/home/qmsmonitor/qmsnotifier3.py"]
