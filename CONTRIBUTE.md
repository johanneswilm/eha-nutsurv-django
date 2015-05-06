# Contribute

Outlined here is our workflow for this project

## Deployment Environments

In addition to every developer's workstation having a development version of
this software, there are three different environments running this software on
a server:

### dev

URL: https://nutsurv-dev.eocng.org/

This server is "for developers". It should not be used by people outside of
the development team.

It's updated from the development branch whenever there is a new pull-request
merged in.

If this sever doesn't work, resolving that should be top priority.

There may be data imported here from the 2014 survey, the database might be
truncated at any time and this instance can be used to reproduce or
demonstrate issues.

### staging

URL: https://nutsurv-staging.eocng.org/

A production like environment showing the current status of the development
efforts. It can be used by all stakeholders, at any time, for demo purposes.

It's updated only from docker images that are built only from tagged releases
that are consideerd release worthy by the development team.

If this server doesn't work, resolving this is top priority, because it's
considered a production system.

No data will be imported here, data entry only works through via API (i.e.
through punching it in the nutsurv-mobile app.)


### production

URL: TBD

Used by real end users, should not be used for demonstration purposes by
anyone. Just real field data and real users are allowed here.

It's updated from the same docker images built from tagged releases that
have been proven solid on staging.

If there is an issue with this server, solving that is top priority.

There will be no csv data import here.

## Initial Setup

1. git clone git@github.com:eHealthAfrica/eha-nutsurv-django

### Creating a new feature, bring your stuff current

2. git checkout develop
3. git pull
4. git checkout -b bnvk/new-feature-branch

### Then ...hack hack hack... then add your code

1. git add path/file
2. git commit -m "message goes here"
3. git push origin bnvk/new-feature-branch

### Login to Github and make a pull request

Wait for your pull request to be accepted.

*Note: if you need to keep working on this feature, bug another dev to merge in your work, otherwise things can get funky*

## Migrating DB Schema

1. ./manage.py reset_db
2. psql -f enable_postgis.sql -h localhost -U postgres
3. psql -f make_nutsurv_dev.sql -h localhost -U postgres
4. ./manage.py migrate
5. ./manage.py createsuperuser
6. ./manage.py import_formhub path/to/file.csv
