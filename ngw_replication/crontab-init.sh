#!/bin/bash

echo "create cron file..."
echo "# " > /etc/cron.d/replication-cron
echo "0 * * * * python /helper_scripts/ngw_replication/ngw_replication.py -url1 "$(cat /run/secrets/2019tigercounter_primary_ngw_url)" -layer1 "$(cat /run/secrets/2019tigercounter_primary_ngw_layer) -login1 $(cat /run/secrets/2019tigercounter_primary_ngw_login) -pass1 $(cat /run/secrets/2019tigercounter_primary_ngw_password) -url2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_url)" -layer2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_layer)" -login2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_login)" -pass2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_password)"  >> /etc/cron.d/replication-cron
echo "0 * * * * python /helper_scripts/ngw_replication/ngw_replication.py -url1 "$(cat /run/secrets/2019tigercounter_primary_ngw_url)" -layer1 "$(cat /run/secrets/2019tigercounter_primary_ngw_layer2) -login1 $(cat /run/secrets/2019tigercounter_primary_ngw_login) -pass1 $(cat /run/secrets/2019tigercounter_primary_ngw_password) -url2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_url)" -layer2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_layer2)" -login2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_login)" -pass2 "$(cat /run/secrets/2019tigercounter_secondary_ngw_password)"  >> /etc/cron.d/replication-cron
echo "# An empty line is required at the end of this file for a valid cron file." >> /etc/cron.d/replication-cron

# Give execution rights on the cron job
chmod 0644 /etc/cron.d/replication-cron

# Apply cron job
crontab /etc/cron.d/replication-cron

echo "Starting cron...."
cron -f
