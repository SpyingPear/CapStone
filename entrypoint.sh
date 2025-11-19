#!/bin/sh
set -e

# Default to local dev DB if not provided
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-news_portal.settings}
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true
python manage.py runserver 0.0.0.0:8000
