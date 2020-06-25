import os
SECRET_KEY = 'fake-key'

# Use nose to run all tests

# Tell nose to measure coverage on the 'foo' and 'bar' apps


INSTALLED_APPS = [

    'mogi',
    'galaxy',
    'gfiles',

    'django_tables2',
    'django_tables2_column_shifter',
    'django_filters',
    'bootstrap3',
    'django_sb_admin',

    'dal',
    'dal_select2',


    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'allauth.socialaccount.providers.google',

    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
DEBUG = True


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

AUTH_USER_MODEL = 'gfiles.User'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test-django-galaxy',
    }
}




STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../mogi"),
)

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

STATIC_URL = '/static/'

#ROOT_URLCONF = 'mogi_site.urls'

LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = '/login/'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_ROOT = '/media/'
MEDIA_URL =  '/media/'


EXTERNAL_DATA_ROOTS = {'TEST': {
                                 'path': os.path.join(BASE_DIR, 'mogi', 'tests', 'data'),
                                 'user_dirs': True,
                                 'help_text': 'test data store',
                                 'filepathfield': False
                                                # if false will use charfield path, if true filepathfield  will look
                                                # recursively in a selected folder but will be to slow for complicated
                                                # folder structure
                       }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(os.path.join(BASE_DIR, 'templates')),
                 ],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
