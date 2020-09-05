FROM python:2.7.13

WORKDIR /site

ADD requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && mkdir /logs/

ADD . .

EXPOSE 8000

CMD bash start.sh
