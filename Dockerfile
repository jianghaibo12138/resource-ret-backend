FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /resource-ret-backend
WORKDIR /resource-ret-backend

# Installing OS Dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y libsqlite3-dev

RUN pip install -U pip setuptools -i https://pypi.douban.com/simple

ADD ./requirements.txt /resource-ret-backend/
ADD ./packages /resource-ret-backend/

RUN pip install -r /resource-ret-backend/requirements.txt -i https://pypi.douban.com/simple
RUN python /resource-ret-backend/django-celery/setup.py install

ADD . /resource-ret-backend
# Django service
EXPOSE 8080