"""
Django settings for nutsurv project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = PROJECT_PATH


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1n=d-2s$)lm44_3logg)&1qh$5i^0j8j1gx3%g!v&9@e56rlv)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

#LOGIN_URL = '/admin'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'dashboard',
    'tastypie',
    'accounts',
    'importer',
    'djangobower',
    'compressor',
    'corsheaders',
    'rest_framework',
    'raven.contrib.django.raven_compat',
]

if DEBUG:
    INSTALLED_APPS.append(
        'django_extensions',
    )

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE_CLASSES = (
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        )

ROOT_URLCONF = 'nutsurv.urls'

WSGI_APPLICATION = 'nutsurv.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'template_postgis',
        'USER': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, '../media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, '../static')

# Bower http://django-bower.readthedocs.org/en/latest/index.html
BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_ROOT, 'components')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
    'compressor.finders.CompressorFinder',
)

BOWER_INSTALLED_APPS = (
    'bootstrap#3.3.2',
    'bootstrap-select#1.6.3',
    'datatables#1.10.4',
    'datatables-bootstrap3-plugin#0.2.0',
    'datatables-responsive#1.0.3',
    'datatables-tabletools#2.2.3',
    'file-saver',
    'jquery#1.10.2',
    'jquery-flot#0.8.3',
    'leaflet#0.7.3',
    'leaflet.markercluster#0.4.0',
    'lodash#3.0.0',
    'parse-python-indentation#0.1.0',
    'eHealthAfrica/ehealth-bootstrap#0.0.5',
    'font-awesome#4.2.0',
    'moment#2.9.0',
    'moment-timezone#0.3.0',
    'list.js#1.1.1',
    'list.pagination.js',
    'jquery.cookie#1.4.1',
    'eHealthAfrica/data-models#1.12.1',
    )



COMPRESS_PRECOMPILERS = (
        ('text/sass', 'sassc "{infile}" "{outfile}"'),
        ('text/scss', 'lib.scssabsolutefilter.SCSSFilter'),
        )


REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
        'DEFAULT_RENDERER_CLASSES': (
            'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
            'rest_framework.renderers.TemplateHTMLRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
            ),
        'DEFAULT_PARSER_CLASSES': (
            'djangorestframework_camel_case.parser.CamelCaseJSONParser',
            'rest_framework.parsers.FormParser',
            'rest_framework.parsers.MultiPartParser',

            ),
        }



try:
    f = open(os.path.join(PROJECT_PATH, 'configuration.py'))
except IOError as e:
    print "Did not load local configuration:", e
    print "That's ok, but you may want to copy the configurations.py-default"
else:
    exec f in globals()
