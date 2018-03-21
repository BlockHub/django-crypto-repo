#!/usr/bin/bash

# Need to ensure we have the correct encodings since we are initializing arky
export LANG=en_US.UTF-8
source /srv/CIP/venv/bin/activate
python /srv/CIP/django-crypto-repo/manage.py bittrexbot
