#!/bin/bash

python manage.py migrate
uwsgi conf/uwsgi/uwsgi.xml
