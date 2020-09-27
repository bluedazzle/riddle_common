#!/bin/bash
python manage.py makemigrations
python manage.py migrate --fake-initial
uwsgi conf/uwsgi/uwsgi.xml
