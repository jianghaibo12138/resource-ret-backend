#!/usr/bin/env bash

python /resource-ret-backend/manage.py migrate
python /resource-ret-backend/manage.py loaddata /resource-ret-backend/admin_json/application.json
python /resource-ret-backend/manage.py runserver 0.0.0.0:8080