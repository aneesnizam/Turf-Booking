#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Add this line to move into your project folder

# These commands will now run correctly
python manage.py collectstatic --no-input
python manage.py migrate