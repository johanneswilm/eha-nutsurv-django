FROM ubuntu:14.04

RUN apt-get install -y wget
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc |  apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
  git \
  postgresql-9.3 \
  postgresql-9.3-postgis-2.1 \ 
  python-psycopg2 \
  python-dev \
  python-numpy \
  python-scipy \
  python-virtualenv

RUN pip install libsass
ADD . /opt/nutsurv
RUN pip install -r /opt/nutsurv/requirements/development.txt
RUN python /opt/nutsurv/nutsurv/manage.py collectstatic --noinput
CMD supervisord -c /opt/nutsurv/config/supervisord.conf
