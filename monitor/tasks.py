#encoding=utf-8

from __future__ import absolute_import
import httplib, urllib
import json
import time
import urlparse
from celery import shared_task
from urllib2 import quote
import chardet

from celery.utils.log import get_task_logger
from django.utils import simplejson as json
from django.dispatch.dispatcher import receiver
from django.dispatch import Signal

from monitor.models import *
from monitor.messages import *
from monitor.utils import *
from monitor.forms import PostRecordForm


from django_sse.redisqueue import send_event

alarm_message = Signal(providing_args=["args", "kwargs"], use_caching=True)

logger = get_task_logger(__name__)

TRANSFER_DICT=dict(website='sitename', 
    title="title", time="time", 
    user_name="author", url="url", 
    ip_and_port="clientip",)

def record(data, char):
    """关联帖子信息和关键字"""
    pass


# def search_and_match(data, chars=[]):
#     """检查是否匹配"""
    #匹配几个词、
    #一旦匹配 写入表、返回结果
    #下游函数收集结果
    #检查是否有结果，有报警
    # if data:
    #     for _id, c in chars:
    #         if not isinstance(data, unicode):
    #             try:
    #                 data = unicode(data, "utf8")
    #                 if not isinstance(c, unicode):
    #                     c = unicode(c, "utf-8")
    #             except Exception, e:
    #                 print "it is not utf8"
    #                 print "in gbk"
    #                 data = unicode(data, "gbk")
    #                 if not isinstance(c, unicode):
    #                     c = unicode(c, "gbk")
    #         if c in data:
    #             record(data, c)
    #             return (True, _id)
    # return (False, "")

def search_and_match(data, chars=[]):
    if data:
        for _id, c in chars:
            if c in data:
                if not isinstance(c, unicode):
                    c.decode('utf-8')
                record(data, c)
                return (True, _id)
    return (False, "")


def is_in(data, chars):
    [lambda x: x in data for _id, c in chars]

def alarm(a_message=[]):
    """警报"""
    users = Contact.objects.all()
    msg = dict(users=users,)
    contacts = Contact.objects.all().values_list("email", flat=True)
    msg = {}

    title = u"%s 网站出现非法关键词“%s”警报提示！" %(site, word)
    do_sendmail(msg=msg, mail_list=contacts, )


def new_alarm(a_message, inform_teams):
    words = []
    users = Contact.objects.all()
    teams = inform_teams
    msg = dict(users=users, )
    #only notify team whose word is alarmed
    contacts = Contact.objects.filter(team__in=teams)
    emails = contacts.values_list("email", flat=True)
    mobiles = contacts.values_list("phone", flat=True)
    #组装email信息
    msg = {"a_message": a_message}
    title = u"网站出现非法关键词警报提示！"
    do_sendmail(msg=msg, mail_list=emails, title=title)
    #组装sms信息并发送
    sms_template = u"系统内发现非法关键词:{0}，请到后台内查看【茶盒互动】"
    words = [a['word'] for a in a_message]
    if len(words) >= 1:
        words = words[0]
    content = sms_template.format(words)
    do_send_sms(mobiles, content)


def urldecode_to_utf8(dict_data):
    for k, v in dict_data.items():
        urldecode_data = urllib.unquote(str(v))
        try:
            unicode_data = unicode(urldecode_data, 'utf-8')
        except Exception, e:
            print "error in urldecode_data encode utf8"
            try:
                unicode_data = unicode(urldecode_data, 'gbk')
            except Exception, e:
                print "error in urldecode_data encode GB2312"
                raise e
        dict_data[k] = unicode_data
    return dict_data


def transfer_dict(d_dict):
    for k, v in TRANSFER_DICT.items():
        if k == 'time':
            d_dict[k] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(d_dict[k])))
        else:
            d_dict[k] = d_dict.pop(v)
    return d_dict

@shared_task
def filter_task(post_data):
    #记录集合
    result = list()
    #警报列表
    a_message = list()
    chars = Words.objects.filter(enabled=True).values_list("id", "word")
    for post in post_data:
        flag, char_id = search_and_match(post['message'], chars)
        #如果有关键字, 则做标记
        if flag:
            post['word'] = int(char_id)
            a_message.append(post)

        _post = transfer_dict(post)
        form = PostRecordForm(_post)
        site = Sites.objects.filter(ip=_post['site_ip'])[0]
        if form.is_valid():
            cleaned_data = form.cleaned_data
            cleaned_data['site'] = site
            if cleaned_data.get('word'):
                word_set = Words.objects.filter(id=cleaned_data['word'])
                cleaned_data["word"] = word_set and word_set[0]
            result.append(AlarmRecord(**cleaned_data))
    
    #批量创建记录
    AlarmRecord.objects.bulk_create(result)
    if a_message:
        inform_teams = gen_2_list(a_message)
        try:
            alarm_message.send(sender=AlarmRecord.__class__, inform_teams=inform_teams)
        except Exception, e:
            raise e
        try:
            new_alarm(a_message, inform_teams)
        except Exception, e:
            raise e 
    
    return result

def gen_2_list(a_message):
    """生成通知的team"""
    words = []
    teams = []
    for a in a_message:
        words.append(Words.objects.get(id=a['word']))
        a['word'] = Words.objects.get(id=a['word']).word
    #add related teams to contact list
    [teams.extend(list(word.team.all())) for word in words ]
    return set(teams)

@receiver(alarm_message, )
def alarm_notify(sender=None, **kwargs):
    inform_teams = kwargs["inform_teams"]
    channels = [team.id for team in inform_teams]
    message = json.dumps({
        'type': 'foo',
        'html': "news",
    })
    for channel in channels:
        send_event('message', message, channel) # named channel
    return True



def test_nofity():
    print "start"
    alarm_message.send(sender=AlarmRecord.__class__,)
    print "end"