CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = False
INSTALLED_APPS += (
        'corsheaders',
        'django_extensions',
        )

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


DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'nutsurv_dev',
            'USER': 'nutsurv_dev',
            'PORT': '5432',
            }
        }


# Add a secret text that has to be added to all posts from formhub.
# This is to increase security as posts from formhub will not hold the CSRF security info.
POST_KEY = ""
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
