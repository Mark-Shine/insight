#encoding=utf-8

from __future__ import absolute_import
import json
import time
from celery import shared_task

from monitor.models import *
from monitor.messages import *


TRANSFER_DICT=dict(website='sitename', 
    title="title", time="time", 
    user_name="author", url="url", 
    ip_and_port="clientip",)

def record(data, char):
    """关联帖子信息和关键字"""
    pass


def search_and_match(data, chars=[]):
    """检查是否匹配"""
    #匹配几个词、
    #一旦匹配 写入表、返回结果
    #下游函数收集结果
    #检查是否有结果，有报警
    for _id, c in chars:
        if not isinstance(c, unicode):
            c = unicode(c, "utf-8")
        if c in data:
            record(data, c)
            return (True, _id)
    return (False, "")


def alarm():
    """警报"""
    users = Contact.objects.all()
    msg = dict(users=users,)
    do_sendmail()
    do_sendsms()



def transfer_dict(d_dict):
    for k, v in TRANSFER_DICT.items():
        if k == 'time':
            d_dict[k] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(d_dict[k])))
        else:
            d_dict[k] = d_dict.pop(v)
    return d_dict

@shared_task
def filter_task(post_data):
    count = len(post_data)
    #记录集合
    result = list()
    #警报列表
    a_message = list()
    chars = Words.objects.values_list("id", "word")
    for index in range(0, count):
        json_post = post_data[str(index)]
        post = json.loads(json_post)
        flag, char_id = search_and_match(post['message'], chars)
        #如果有关键字, 则做标记
        if flag:
            post['word'] = int(char_id)
            a_message.append(post)
            try:
                alarm()
            except Exception, e:
                raise e
        _post = transfer_dict(post)
        result.append(AlarmRecord(**_post))
    #批量创建记录
    AlarmRecord.objects.bulk_create(result)
    return result
