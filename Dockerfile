FROM ubuntu:14.04

RUN apt-get install -y wget
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc |  apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && apt-get -y upgrade && apt-get install -y gfortran libopenblas-dev liblapack-dev python-numpy python-scipy nodejs-legacy libgeos-dev npm git postgresql-9.3 postgresql-9.3-postgis-2.1 python-virtualenv python-dev libpq-dev postgresql-server-dev-all gfortran libopenblas-dev liblapack-dev

ADD . /opt/nutsurv
RUN pip install -r /opt/nutsurv/requirements/development.txt
RUN npm install bower
CMD python /opt/nutsurv/nutsurv/manage.py shell
