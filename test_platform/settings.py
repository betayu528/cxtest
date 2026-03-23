from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CELERY_DIR = BASE_DIR / ".celery"
for folder in ("in", "out", "processed"):
    (CELERY_DIR / folder).mkdir(parents=True, exist_ok=True)

SECRET_KEY = "django-insecure-typkah7n+*awe3p1qxp^(+a^!n=tu*b0&yv&^2qb0fx9p(j4!="
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "projects",
    "cases",
    "api_testing",
    "async_tasks",
    "mockserver",
    "datahub",
    "bugs",
    "knowledge",
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "test_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "test_platform.wsgi.application"
ASGI_APPLICATION = "test_platform.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
PLATFORM_INTERNAL_AUTH_HEADER = "X-Platform-Auth"
PLATFORM_INTERNAL_USER_HEADER = "X-Platform-User"
PLATFORM_INTERNAL_ROLE_HEADER = "X-Platform-Role"
PLATFORM_INTERNAL_AUTH_TOKEN = "platform-internal-demo-token"

CELERY_BROKER_URL = "filesystem://"
CELERY_RESULT_BACKEND = "cache+memory://"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 30
CELERY_TASK_DEFAULT_QUEUE = "platform"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "data_folder_in": str(CELERY_DIR / "in"),
    "data_folder_out": str(CELERY_DIR / "out"),
    "data_folder_processed": str(CELERY_DIR / "processed"),
}
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True
