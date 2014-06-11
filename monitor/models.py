#encoding=utf-8
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from monitor.signals import after_action
from django.dispatch import receiver


class Team(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self,):
        return self.name

# Create your models here.
class Words(models.Model):
    """关键字"""
    word = models.CharField(max_length=32)
    nums = models.IntegerField(blank=True, null=True)
    enabled = models.BooleanField(blank=True, default=True)
    team = models.ManyToManyField("Team", blank=True, null=True,)
    
    def __unicode__(self,):
        return u"关键词: %s-%s" %(self.id, self.word)


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
    position = models.CharField(max_length=8, blank=True, null=True, default='')
    #状态
    state = models.IntegerField(blank=True, default=0, choices=((0, u"未处理"), (1, "已处理")))

    def __unicode__(self,):
        return u"警告记录: %s-%s" %(self.id, self.title)



class ActionRecord(models.Model):
    """docstring for ActionRecord"""
    action = models.CharField(max_length=24, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    message = models.CharField(max_length=64, blank=True, null=True)

    @receiver([after_action],)
    def record_handel(sender=None, user=None, instance=None, action=None, **kwargs):
        form = {}
        form['user'] = user
        form['message'] = instance
        form['time'] = datetime.datetime.now()
        form['action'] = action
        acrecord, created = ActionRecord.objects.get_or_create(**form)


class Contact(models.Model):
    """联系人表"""
    name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=64, blank=True, null=True)
    recieve_email = models.CharField(max_length=8, blank=True, null=True)
    recieve_sms = models.CharField(max_length=8, blank=True, null=True)
    team = models.ForeignKey(Team, blank=True, null=True)

    def __unicode__(self,):
        return u"联系人: %s-%s" %(self.id, self.name)

class Sites(models.Model):
    """监控的网站"""
    ip = models.CharField(max_length=64, blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    #是否启用
    enabled = models.BooleanField(blank=True, default=True)
    team = models.ForeignKey(Team, blank=True, null=True)

    def __unicode__(self,):
        return u"监控站点: %s-%s" %(self.id, self.ip)





