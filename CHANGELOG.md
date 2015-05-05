# [Changelog](https://github.com/eHealthAfrica/eha-nutsurv-django/releases)

## [0.10.2](https://github.com/eHealthAfrica/eha-nutsurv-django/compare/0.10.2...0.10.2)

* [5d580b7](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5d580b7) Fix map not loading under https

## [0.10.1](https://github.com/eHealthAfrica/eha-nutsurv-django/compare/0.10.1...0.10.1)

* [2e6ebf4](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2e6ebf4) Add locations to alerts that need it
* [2f0ee97](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2f0ee97) don't put Point objects on the line for json.dumps
* [29ad4bc](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/29ad4bc) New initial migrations
* [417e7dd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/417e7dd) Fixes #405, clean migration restart
* [cb572f4](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/cb572f4) Revert change of how HouseholdMembers are saved
* [5c6c616](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5c6c616) add alert types to frontend code
* [e493dca](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e493dca) don't break on not finding cluster for second admin level check either
* [ae492af](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ae492af) remove json structure from alerts and tests for 1st and 2nd admin level region
* [52789dd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/52789dd) Query optimization for household member
* [a070db5](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/a070db5) remove deletion of cluster document from test
* [edbcf79](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/edbcf79) make flake8 happy
* [9eb81ae](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/9eb81ae) add tests
* [5d5c301](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5d5c301) Add more extra_questions tests, don't show household memeber url
* [7719ad9](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/7719ad9) Added test for household member API call
* [c7bbee5](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c7bbee5) Update Travis to use Postgres 9.4 for JSONB
* [302104c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/302104c) Added more extra_questions tests, added url helper for HouseholdMember
* [83a5a38](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/83a5a38) add check for first admin level, fixes issue #304
* [bc3792d](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/bc3792d) Fixed serializers and added tests for extra_data
* [ddcab05](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ddcab05) (wip) Added Extra Questions
* [5e2de0f](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5e2de0f) Fix import paths for testing
* [349e51c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/349e51c) add minimal raven.js config for dev/staging
* [46f349d](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/46f349d) configure .request context processor
* [5bd2cc5](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5bd2cc5) add raven.js dependency via bower
* [4e0c52b](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/4e0c52b) Fix #325 Added changlog
* [ab9b7a9](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ab9b7a9) add instructions for install of nodejs and npm, fixes #397

## [v0.10.0](https://github.com/eHealthAfrica/eha-nutsurv-django/compare/v0.10.0...v0.10.0)

* [7bc20a5](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/7bc20a5) Fix alert generation
* [dcac9d4](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/dcac9d4) use pk for TeamMember urls and not for Alerts
* [3f0270a](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/3f0270a) Clean up migrations and tests
* [4080ccd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/4080ccd) Remove member_id
* [2079acd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2079acd) Expose 'index' property for training subjects
* [9e0de85](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/9e0de85) Fix alert generation
* [2718960](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2718960) update test for new API
* [56cd00b](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/56cd00b) +simple 'mapping_check_missing_cluster' alert test
* [96dc256](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/96dc256) Split mapping_check_alert in 4 methods
* [c4edb7c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c4edb7c) delete all existing JSONfield migrations
* [e52d278](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e52d278) Discourage jsonfield.fields.JSONfield migrations
* [32bb4eb](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/32bb4eb) make teammember's mobile optional
* [c0ad0aa](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c0ad0aa) added modal for Personnel / Last Survey, fixes: 381
* [f5a377e](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/f5a377e) remove get_household_member_records function
* [e71d0ac](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e71d0ac) re-did CSV exporting, fixes #380
* [5b8a379](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5b8a379) Clarify the mobile app is optional in README
* [ae58487](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ae58487) finished major changes to Personnel styling, fix #276
* [f03c79b](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/f03c79b) migrate point to location
* [54ea77b](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/54ea77b) test whether surveys without locations can save
* [c602b70](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c602b70) rename Survey.point to .location
* [6535f4e](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6535f4e) 6:00 AM is the new 7:00 AM (spec adjustment)
* [867877a](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/867877a) Fixes #374 Increases the length of a few fields
* [3a7cf1f](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/3a7cf1f) fix bug with .get_or_create_alert's signature
* [750067f](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/750067f) adjust to new alert creation structure
* [dcbdd85](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/dcbdd85) add number_of_children alert, for issue #307
* [5617aa8](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5617aa8) fixed path to SCSS in compressor thanks to @tremolo help
* [97ca761](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/97ca761) updated README
* [99a89e0](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/99a89e0) Add build step
* [ecf3f01](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ecf3f01) Update README and travis
* [1edc6c2](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/1edc6c2) updated base.html with datatables code
* [f21071a](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/f21071a) merged Personnel & Training into a dropdown Nav item
* [fffa73f](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/fffa73f) also use .get_or_create_alert here
* [388f71b](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/388f71b) add a few blank lines for better readability
* [09359d0](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/09359d0) perform 'extract method' on copy-pasted code
* [0b05fdb](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/0b05fdb) Be explicit on training fields to show
* [dd4a38c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/dd4a38c) made a bit of progress on styling up Personnel as per #276
* [964ccbc](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/964ccbc) Added geojson field to survey model and serializer
* [5049320](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5049320) Added nutsurv branding to api, add optional debug_toolbar to urls
* [9e1494d](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/9e1494d) Update travis for new db settings; update gitignore for bower
* [360ddfd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/360ddfd) Update readme install
* [c580796](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c580796) Use a proper icon for training module
* [d773753](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/d773753) Use pytest
* [2bae89d](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2bae89d) Allow team members to be modifed over the apain again, improve tests
* [6ee15da](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6ee15da) Make team_lead household survey specific,
* [2d92f78](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2d92f78) add alerts for missing data, related to #305
* [ddce5ce](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ddce5ce) fix(survey) Fix #353 nest the last survey in the team member
* [e3c8aa4](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e3c8aa4) fix(survey) Fix #353 Add first and second admin level fields
* [1a2c5ff](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/1a2c5ff) feature(teams) Prevent modifying or deleting teammembers on api
* [50383db](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/50383db) dumb down training room view to follow spec
* [6fd6a7a](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6fd6a7a) muac/height/weight are optional
* [b739a75](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/b739a75) fix initial training migrations
* [9905e97](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/9905e97) Provide initial migrations for training
* [dba090d](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/dba090d) add migrations for dashboard
* [32243b8](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/32243b8) make gender/name/birthdate optional for hh members
* [6b72e0e](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6b72e0e) fix: #347 fixed typo naming of class, removed uneeded arg
* [0d23430](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/0d23430) fix(survey) Fix #346 allow no auth for the training room survey
* [c84413c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c84413c) fix: #341 home feed alert marking as completed
* [0397e43](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/0397e43) fix(alerts) Make sure the nested TeamMember is read only
* [c5b9952](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c5b9952) docker db image: use postgres 9.3 for +consistency
* [8af56bf](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/8af56bf) Fix travis database config
* [8f1a135](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/8f1a135) refactored how Contact Team modal is rendered, fix #341
* [ae3313e](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ae3313e) fix(training_urls) Some of the dashboard urls needed to be moved to the training
* [e1f141f](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e1f141f) pin lodash to 3.0.0
* [6d6bd30](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6d6bd30) Update travis, only lint the nutsurv dir
* [702bc4e](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/702bc4e) Use relative STATICFILES_DIRS
* [d3f970c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/d3f970c) made some progress with Personnel design as per issue #276
* [c88d5ed](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c88d5ed) fix(paths) New deploy needed tweaks to settings
* [d79cf41](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/d79cf41) chore(migrations) Add missing migration
* [5bd4056](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5bd4056) fix(teammembers) Fix #279 the pk was being set manually. No no.
* [8c0a5c0](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/8c0a5c0) remove django-bower dependency
* [cc25129](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/cc25129) split page reload timer from data_getter
* [edd30b6](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/edd30b6) updated installation instructions, use bower separately and not through django
* [07a05cd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/07a05cd) fix for import problem of scipy.stats
* [4d96f18](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/4d96f18) fix(dashboard) Add last survey data to the team member
* [fa0188a](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/fa0188a) fix: symlink psycopg2 module into virtualenv
* [1b14dae](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/1b14dae) fix: forgot to cd to project dir
* [e197811](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e197811) adapt travis setup to new deployment setup
* [dd4c310](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/dd4c310) install more modules with apt-get instead of pip to reduce image size and build size. the bower_components are now expected to be in nutsurv/components/bower_components berfore building the docker images, either by running bower install manually or by using the build server.
* [3cde15e](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/3cde15e) add bower.json instead of installing through django
* [9ab1ddb](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/9ab1ddb) Update README with how to do linting
* [aa3e38a](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/aa3e38a) Fix formating
* [b1d6f9c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/b1d6f9c) Update travis for flake8 and add it to requirements
* [2e91ecd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2e91ecd) Don't pep8 migrations
* [f880ad0](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/f880ad0) Fix #302 lint and pep8
* [a218fca](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/a218fca) fix bug where checkmark would appear w/ no records
* [03ed7f1](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/03ed7f1) checkmarks are green now (as per the spec)
* [96371ff](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/96371ff) Add super-simplistic web view that uses cli import
* [5555ff6](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5555ff6) split management command in open file/handle file
* [92b3daf](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/92b3daf) training test data: only have 10 subjects here
* [141e43c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/141e43c) import hh members as camel case in json field
* [a327a45](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/a327a45) move training javascript to their own files
* [9f98e24](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/9f98e24) tab for training; bump font-awesome for icon
* [cc76c1c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/cc76c1c) simple testdata for training module!
* [d08a8db](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/d08a8db) add ?member_detail modifier to /training/rooms/\d/
* [edbe621](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/edbe621) Training module
* [f52a79e](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/f52a79e) Rename HouseholdMember field
* [860419b](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/860419b) use non-minified version of of js dependencies



## [0.9.0](https://github.com/eHealthAfrica/eha-nutsurv-django/compare/0.9.0...0.9.0)


* [af7d9c1](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/af7d9c1) Add migrations for training module prep
* [c456245](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c456245) add team_name as well
* [4f8f454](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/4f8f454) add team_id, fixes #312
* [dfc929f](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/dfc929f) allow team leader id = 0 in dashboard filters, fixes #284
* [8733f8a](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/8733f8a) add gender from fake data
* [5f25546](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5f25546) add migrations
* [29e6a72](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/29e6a72) Cascade deletes of team to alerts
* [7e9c552](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/7e9c552) Added migrations
* [66d35f1](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/66d35f1) rm text field in alert because bnvk is sad
* [e2873d8](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e2873d8) part of #291 Removed team name and id add relation to team_lead and survey
* [c6cbf51](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/c6cbf51) Fix #291 add team lead in alert
* [fade7f9](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/fade7f9) fixed merge
* [982ad78](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/982ad78) add migrations
* [efde103](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/efde103) Update Dockerfile
* [3e16c1c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/3e16c1c) limited last contacted alerts on dashboard, fixes #277
* [6bb6e86](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6bb6e86) Update Docker file.
* [0a92ba9](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/0a92ba9) really
* [6e56bc8](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6e56bc8) Fix #289 server static files from uwsgi
* [170d048](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/170d048) docker compose with up and not run
* [5d57ea0](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/5d57ea0) Fixes #285 and allows anon team access
* [e16b5ff](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e16b5ff) Fix #286, properly wrap json spec function
* [91d9b44](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/91d9b44) Fix #282 configure logging
* [d913d81](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/d913d81) added import test data step to README
* [6b80ea4](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6b80ea4) Add HouseholdMember relational model
* [7099364](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/7099364) Add ABC for HouseholdSurveyJSON
* [1925b19](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/1925b19) Add household_number field to HouseholdSurveyJSON
* [99b0a8c](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/99b0a8c) add django-debug-toolbar for development
* [78603af](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/78603af) Add nitpicky TODO directed at @readevalprint
* [2d538dd](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/2d538dd) -- fix comma placement (OCD FTW!)
* [66b088b](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/66b088b) Only expose HHSurvey's relational fields
* [add57f8](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/add57f8) look up member_id on TeamMember, not HHSurvey
* [6ace479](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/6ace479) test more empty endpoints
* [b4be0f6](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/b4be0f6) use relative imports
* [ff92034](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ff92034) use relative imports in dashboard.urls
* [ef1f0ed](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/ef1f0ed) Fixes 248 adds data-model dependency, and loads NutritionSurvey.json
* [e4a9712](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e4a9712) Fix #271 and fix #272 with simplified docker instructions
* [67c36b5](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/67c36b5) More js templates and references
* [e25c413](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/e25c413) Fix #262 fix mixedCase js templates
* [d6c8c17](https://github.com/eHealthAfrica/eha-nutsurv-django/commit/d6c8c17) Change the FakeTeams to match json spec
