import os
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR/'.env')
def env_bool(name, default='False'):
 return os.getenv(name, default).strip().lower() in ('1','true','yes','on')

SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','unsafe-development-key')
DEBUG=env_bool('DJANGO_DEBUG','False')
if not DEBUG and (not SECRET_KEY or SECRET_KEY == 'unsafe-development-key' or SECRET_KEY == 'local-development-key-change-before-deployment'):
 raise ImproperlyConfigured('Set a unique DJANGO_SECRET_KEY environment variable when DJANGO_DEBUG=False.')
ALLOWED_HOSTS=[x.strip() for x in os.getenv('DJANGO_ALLOWED_HOSTS','127.0.0.1,localhost').split(',') if x.strip()]
RENDER_EXTERNAL_HOSTNAME=os.getenv('RENDER_EXTERNAL_HOSTNAME','').strip()
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
 ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if x.strip()]
if RENDER_EXTERNAL_HOSTNAME:
 CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')
LANGUAGE_CODE='en-in'
TIME_ZONE=os.getenv('TIME_ZONE','Asia/Kolkata')
USE_I18N=True
USE_TZ=True
INSTALLED_APPS=[
'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
'accounts.apps.AccountsConfig','academics','lessons','homework','exams','attendance','timetable','fees','notifications','administration','students','Teachers','Parents','common']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','config.context_processors.academix']}}]
WSGI_APPLICATION='config.wsgi.application'
ASGI_APPLICATION='config.asgi.application'
db=os.getenv('DATABASE_URL','sqlite:///'+str(BASE_DIR/'db.sqlite3'))
if db.startswith('postgres://'): db=db.replace('postgres://','postgresql://',1)
if db.startswith('postgresql://'):
 p=urlparse(db)
 query=parse_qs(p.query)
 db_options={}
 if query.get('sslmode'):
  db_options['sslmode']=query['sslmode'][0]
 DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':unquote(p.path.lstrip('/')),'USER':unquote(p.username or ''),'PASSWORD':unquote(p.password or ''),'HOST':p.hostname or 'localhost','PORT':p.port or 5432,'CONN_MAX_AGE':60,'OPTIONS':db_options}}
elif db.startswith('sqlite:///'): DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':db.removeprefix('sqlite:///')}}
else: raise ValueError('DATABASE_URL must be postgresql://... or sqlite:///path')
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
STATIC_URL='static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[BASE_DIR/'static']
MEDIA_URL='media/'
MEDIA_ROOT=BASE_DIR/'media'
LOGIN_URL='login'
LOGIN_REDIRECT_URL='dashboard'
LOGOUT_REDIRECT_URL='login'
STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage' if DEBUG else 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
SESSION_COOKIE_HTTPONLY=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS='DENY'
SECURE_SSL_REDIRECT=env_bool('SECURE_SSL_REDIRECT', 'False') and not DEBUG
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
CSRF_COOKIE_SECURE=not DEBUG
SESSION_COOKIE_SECURE=not DEBUG
SECURE_HSTS_SECONDS=int(os.getenv('SECURE_HSTS_SECONDS', '31536000' if not DEBUG else '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS=not DEBUG
SECURE_HSTS_PRELOAD=not DEBUG
SECURE_REFERRER_POLICY='same-origin'
DATA_UPLOAD_MAX_MEMORY_SIZE=10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE=10 * 1024 * 1024
