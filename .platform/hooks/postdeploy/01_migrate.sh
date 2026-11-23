#!/bin/bash
set -e
cd /var/app/current

PYTHON=$(find /var/app/venv -name python3 -type f | head -n 1)
if [ -z "$PYTHON" ]; then
    PYTHON=$(ls -d /var/app/venv/*/bin/python | head -n 1)
fi

echo "Using Python executable: $PYTHON"
$PYTHON manage.py migrate --noinput
$PYTHON manage.py collectstatic --noinput
