FROM python:3.6.9

WORKDIR /data/github.com/ReflecBeatCustom/Rebellio
COPY . /data/github.com/ReflecBeatCustom/Rebellio

# Install requirements
RUN pip install django pymysql django-simple-captcha

WORKDIR /data/github.com/ReflecBeatCustom/Rebellio/Rebellio
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8080"]