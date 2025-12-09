#!/usr/bin/env bash
# Exit on first error
set -e

# Install all required packages
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate --noinput
