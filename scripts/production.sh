#!/usr/bin/env bash

python /resource-ret-backend/manage.py migrate
python /resource-ret-backend/manage.py collectstatic --noinput
uwsgi /resource-ret-backend/uwsgi.ini