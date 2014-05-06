#encoding=utf-8
from django.db import models

# Create your models here.


class Account(models.Model):
    """关键字"""
    name = models.CharField(max_length=64, blank=True, null=True)
    password = models.CharField(max_length=12, blank=True, null=True)
    email = models.EmailField(blank=True,)
    tel = models.CharField(max_length=13, blank=True) 
    #是否开启邮件、短信通知  
    email_enable = models.IntegerField(blank=True,)
    sms_enable = models.IntegerField(blank=True,)

class ActionRecord(models.Model):
    # rd_name = models.CharField()
    pass