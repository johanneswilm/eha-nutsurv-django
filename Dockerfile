FROM ubuntu:14.04

RUN apt-get install -y wget
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc |  apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
  gfortran \
  git \
  libgeos-dev \
  liblapack-dev \
  libopenblas-dev \
  libpq-dev \
  nodejs-legacy \
  npm \
  postgresql-9.3 \
  postgresql-9.3-postgis-2.1 \ 
  postgresql-server-dev-all 
  python-dev \
  python-numpy \
  python-scipy \
  python-virtualenv \

RUN pip install libsass psycopg2
ADD . /opt/nutsurv
RUN pip install -r /opt/nutsurv/requirements/development.txt
RUN npm install -g bower

CMD supervisord -c /opt/nutsurv/config/supervisord.conf
