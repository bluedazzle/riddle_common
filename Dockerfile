FROM python:2.7.13
ADD . /site

WORKDIR /site
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && mkdir /logs/
EXPOSE 8000