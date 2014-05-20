#encoding=utf-8
from django.db import models

# Create your models here.
class Words(models.Model):
    """关键字"""
    word = models.CharField(max_length=32)
    nums = models.IntegerField(blank=True, null=True)
    enabled = models.BooleanField(blank=True, default=True)


class Website(models.Model):
    """观察网站"""
    name = models.CharField(max_length=64, blank=True, null=True)
    host = models.CharField(max_length=64, blank=True, null=True)


class AlarmRecord(models.Model):
    """警报记录表"""
    website = models.CharField(max_length=64, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=128, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    user_name = models.CharField(max_length=64, blank=True, null=True)
    url = models.CharField(max_length=128, blank=True, null=True)
    #端口和ip
    ip_and_port = models.CharField(max_length=32, blank=True, null=True)
    #关键字
    word = models.IntegerField(blank=True, null=True)


class Contact(models.Model):
    """联系人表"""
    name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    recieve_email = models.CharField(max_length=8, blank=True, null=True)
    recieve_sms = models.CharField(max_length=8, blank=True, null=True)

class Sites(models.Model):
    """监控的网站"""
    host = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    #是否启用
    enabled = models.BooleanField(blank=True, default=True)


