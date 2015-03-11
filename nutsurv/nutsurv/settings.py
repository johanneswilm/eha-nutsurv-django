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

INSTALLED_APPS = (
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
    'djangobower'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
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
        'NAME': 'nutsurv_dev',
        'USER': 'nutsurv_dev',
        'PASSWORD': 'nutsurv_dev_password',
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

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, '../static')

# Bower http://django-bower.readthedocs.org/en/latest/index.html
BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_ROOT, 'dashboard')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
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
    'lodash#3.0.0',
    'parse-python-indentation#0.1.0',
    'git@github.com:eHealthAfrica/ehealth-bootstrap.git#0.0.2',
    'font-awesome#4.2.0'
)

try:
    exec open(os.path.join(PROJECT_PATH, 'configuration.py')) in globals()
except:  # todo: change this exception to something more specific
    pass
