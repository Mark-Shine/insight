#encoding=utf-8
from django.contrib.auth.models import User, UserManager
from django.db import models
from monitor.models import Words, Team
from django.db.models.signals import post_save

# Create your models here.


class Account(models.Model):
    """关键字"""
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, blank=True, null=True)
    is_admin = models.BooleanField('admin status', default=False,)

    def __unicode__(self,):
        return u"用户：%s-%s" %(self.user.id, self.user.username)

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Account"


    # def create_user_profile(sender, instance, created, **kwargs):  
    #     if created:  
    #        profile, created = Account.objects.get_or_create(user=instance)      

    # post_save.connect(create_user_profile, sender=User) 
    # tel = models.CharField(max_length=13, blank=True) 
    #是否开启邮件、短信通知  
    # email_enable = models.IntegerField(blank=True, null=True)
    # sms_enable = models.IntegerField(blank=True, null=True)
    # 
    # weights = models.IntegerField(blank=True, default=0)


class ActionRecord(models.Model):
    # rd_name = models.CharField()
    pass