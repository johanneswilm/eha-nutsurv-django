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

If this sever doesn't work, resolving that should be a priority.

There may be data imported here from the 2014 survey, the database might be
truncated at any time and this instance can be used to reproduce or
demonstrate issues.

### staging

URL: https://nutsurv-staging.eocng.org/

A production like environment showing the current status of the development
efforts. It can be used by all stakeholders, at any time, for demo purposes.

It's updated only from docker images that are built only from tagged releases
that are consideerd release worthy by the development team.

If this server doesn't work, resolving this has priority, because it's
considered a production system.

No data will be imported here, data entry only works through via API (i.e.
through punching it in the nutsurv-mobile app.)


### production

URL: https://nutsurv.eocng.org/

Used by real end users, should not be used for demonstration purposes by
anyone. Just real field data and real users are allowed here.

It's updated from the same docker images built from tagged releases that
have been proven solid on staging.

If there is an issue with this server, solving that is top priority.

There will be no csv data import here.

## Branching and tagging strategy

The latest and greatest version of the software is in the `develop` branch
(currently not called `master` for historical reasons). Developers should fork
off this branch for new feature branches. This branch is considered stable,
working software, i.e. developers are encouraged to ensure that this is still
the case before merging into this branch by all means (manual checking,
continous integration, code review, etc.). If there is a severe defect in
`develop`, developers need to resolve it immediately or use `git revert` on
the commit introducing the defect, if applicable.

Tagged releases are created by asking for consensus within the development
team that that the most recent commit is release worthy. Important things to
check for are migrations (if the data models changed), changelog, backwards
compatibility with nutsurv-mobile, etc. If all conditions are met, use `git
tag v$VERSION` to tag a release. Also use `git branch -b releases/v$VERSION`
to create a release branch. Build a docker image from that and deploy it to
staging.

Hotfixes are made as commits to the `releases/v$VERSION` branch, then tagged
as `v$VERSION.$PATCHVERSION`. After that has been released to staging, also
consider adding that commit to `develop`.

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
