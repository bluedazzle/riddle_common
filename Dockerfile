FROM python:3.6.0

WORKDIR /site

ADD requirements.txt .
RUN pip3 install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com && mkdir /logs/

ADD . .

EXPOSE 8000

CMD bash start.sh
