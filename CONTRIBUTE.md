# Contribute

Outlined here is our workflow for Github on thus project


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
