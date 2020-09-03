FROM python:2.7.13
ADD . /site

WORKDIR /site
RUN pip install -r requirements.txt
CMD uwsgi conf/uwsgi.xml