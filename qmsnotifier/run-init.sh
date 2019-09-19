#!/bin/bash

echo "$SETUP_CRON root /home/qmsnotifier/run.sh > /proc/1/fd/1 2>/proc/1/fd/2" > /etc/cron.d/qmsnotifier-cron
chmod 0644 /etc/cron.d/qmsnotifier-cron

echo "Starting cron....Waiting for execution..."

cron -f
