#!/bin/bash

echo "create cron file..."

echo "0 * * * * python /home/qmsmonitor/qmsnotifier3.py" > /etc/cron.d/replication-cron
echo "# An empty line is required at the end of this file for a valid cron file." >> /etc/cron.d/replication-cron

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/replication-cron

# Apply cron job
crontab /etc/cron.d/replication-cron

echo "Starting cron...."
cron -f
