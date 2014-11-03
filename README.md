eha-nutsurv-django
==================

NutSurv - Data collection and quality assurance tools for Nutrition Surveys on mobile devices

# Installation


The following has been tested on Ubuntu 14.04. Other versions of Linux/Ubuntu or Mac OS X will have
to make minor adjustments.

First install all needed dependencies:

    sudo apt-get install git postgresql-9.3 postgresql-9.3-postgis-2.1 python-virtualenv python-dev
    libpq-dev postgresql-server-dev-all

Then get the sources (enter username/password):

    git clone https://github.com/eHealthAfrica/eha-nutsurv-django.git nutsurv

Now create a python virtual environment:

    virtualenv --no-site-packages nutsurv-venv

Activate the virtual env (has to be done every time you want to run the application)

    source nutsurv-venv/bin/activate

Enter the source code:

    cd nutsurv

Either install python requirements for a production environment:

    pip install -r requirements/production.txt

or for development:

    pip install -r requirements/development.txt

Create the database nutsurv_dev (ignore the errors) and enable Postgis:

    sudo -u postgres psql -f make_nutsurv_dev.sql
    sudo -u postgres psql -d nutsurv_dev -f enable_postgis.sql

Enter the application:

    cd nutsurv

Add structure to the database:

    ./manage-test.py migrate
