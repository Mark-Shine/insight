#coding=utf-8
import os
from django.utils import importlib


_settings_name = os.environ['DJANGO_SETTINGS_MODULE']
SETTINGS = importlib.import_module(_settings_name)
CONTEXT_PATH = SETTINGS.CONTEXT_PATH
UPLOAD_PATH = SETTINGS.UPLOAD_PATH
#邮件相关
EMAIL_CONTEXT_PATH = SETTINGS.EMAIL_CONTEXT_PATH
