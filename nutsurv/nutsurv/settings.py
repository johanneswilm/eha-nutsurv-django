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

try:
    # For zero downtime deploys
    import uwsgi
    from uwsgidecorators import timer
    from django.utils import autoreload

    @timer(3)
    def change_code_gracefull_reload(sig):
        if autoreload.code_changed():
            uwsgi.reload()

except Exception as e:
    print e


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
    'djangobower',
    'compressor',
    'corsheaders',
    'rest_framework',
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

MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, '../media')

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
    'lodash#3.0.0',
    'parse-python-indentation#0.1.0',
    'git@github.com:eHealthAfrica/ehealth-bootstrap.git#0.0.5',
    'font-awesome#4.2.0',
    'moment#2.9.0',
    'moment-timezone#0.3.0'
)



COMPRESS_PRECOMPILERS = (
        ('text/sass', 'sassc "{infile}" "{outfile}"'),
        ('text/scss', 'sassc -m -I components/bower_components/ehealth-bootstrap "{infile}" "{outfile}"'),
        )

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}


try:
    f = open(os.path.join(PROJECT_PATH, 'configuration.py'))
except IOError as e:
    print "Did not load local configuration:", e
    print "That's ok, but you may want to copy the configurations.py-default"
else:
    exec f in globals()
