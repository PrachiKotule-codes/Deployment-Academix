#!/usr/bin/env bash
# Render build command. Initial migrations must be generated locally and committed first.
set -euo pipefail
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py check
python manage.py check --deploy
# Migrations must be generated locally and committed before deployment.
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py collectstatic --noinput
if [ "${ACADEMIX_SEED_DEMO_DATA:-false}" = "true" ]; then
  python manage.py seed_demo
fi
