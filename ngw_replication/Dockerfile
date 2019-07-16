FROM ubuntu:18.04
MAINTAINER Artem Svetlov <trolleway@yandex.ru>
RUN apt-get update
RUN apt-get install -y python \
python-pip \
git \
cron \
software-properties-common



RUN git clone https://github.com/nextgis/helper_scripts.git
WORKDIR helper_scripts/ngw_replication
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD crontab-init.sh crontab-init.sh
RUN chmod +x crontab-init.sh

CMD ["./crontab-init.sh"]
