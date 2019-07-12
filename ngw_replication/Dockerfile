FROM ubuntu:18.04
MAINTAINER Artem Svetlov <trolleway@yandex.ru>
RUN apt-get update
RUN apt-get install -y python \
python-pip \
git \
cron \
software-properties-common



RUN git clone https://github.com/nextgis/helper_scripts.git
RUN echo "* * * * * python /helper_scripts/ngw_replication/ngw_replication.py -url1 "http://dev.nextgis.com/sandbox" -layer1 247 -login1 administrator -pass1 demodemo -url2 "http://dev.nextgis.com/sandbox" -layer2 491 -login2 administrator -pass2 demodemo" > /etc/cron.d/replication-cron
RUN echo "# An empty line is required at the end of this file for a valid cron file." >> /etc/cron.d/replication-cron


# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/replication-cron

# Apply cron job
RUN crontab /etc/cron.d/replication-cron


CMD ["cron", "-f"]
