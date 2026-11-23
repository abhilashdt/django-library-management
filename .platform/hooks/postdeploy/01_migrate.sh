#!/bin/bash
set -e
cd /var/app/current

# Activate the Elastic Beanstalk Python virtual environment
source /var/app/venv/*/bin/activate

# Apply database migrations to create SQLite tables
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput
