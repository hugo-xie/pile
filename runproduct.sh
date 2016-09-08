#!/bin/bash

# dir starts from application folder
export PRODUCTION_SETTINGS=production.py

cd "$(dirname "$0")"

gunicorn -c gunicorn.conf application:app
