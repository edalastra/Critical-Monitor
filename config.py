import os

DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = True
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
SECRET_KEY = os.environ.get('SECRET_KEY')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')