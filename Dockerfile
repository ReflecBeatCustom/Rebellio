FROM python:3.6.9

WORKDIR /data/github.com/ReflecBeatCustom/Rebellio
COPY . /data/github.com/ReflecBeatCustom/Rebellio

# Install requirements
RUN pip install django
RUN pip install pymysql
RUN pip install django-simple-captcha

ENTRYPOINT ["/bin/bash"]