#encoding=utf-8
import requests
import httplib, urllib
import time
import chardet
from copy import deepcopy
from django.utils import timezone
from django.db import connection
from django.utils.timezone import utc
from django.shortcuts import render
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from django.template.context import (Context, RequestContext)
from django.utils.safestring import mark_safe
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Sites
import json


from .tasks import filter_task


def multiply(request):
    x = int(request.GET['x'])
    y = int(request.GET['y'])
    result = x * y
    response = {'status': 'success', 'retval': result}
    return HttpResponse(dumps(response), mimetype='application/json')

def urldecode_to(dict_data):
    new = {}
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
        new[str(k)] = unicode_data
    return new

def trans_encoding(raw_data):
    new = []
    count = len(raw_data)
    for index in range(0, count):
        v = raw_data[str(index)]
        json_data = json.loads(v)
        new.append(urldecode_to(json_data)) 
    return new

def append_site_ip(data, ip):
    for vo in data:
        vo.update(site_ip=ip)
    return data

@csrf_exempt
def recieve_data(request):
    raw = request.POST
    try:
        data = trans_encoding(raw)
    except Exception, e:
        print "trasn error"
        print e
    try:
        #获取许可的站点
        sites = Sites.objects.all().values_list('ip', flat=True)
        request_ip = request.META['REMOTE_ADDR']
        if request_ip not in sites:
            print "ip %s  not allowed" % request_ip
            return HttpResponse('not allowed')
        data = append_site_ip(data, request_ip)
        filter_task.delay(data)
    except Exception, e:
        print "error: %s" % e
      
    return HttpResponse('ok')


def test():
    begin = time.time()
    for i in range(0, 100000):
        data = {'ip':'127.0.0.1:8080', 'word': "128.0.0.%s" % i}
        url = 'http://127.0.0.1:8080/test'
        r = requests.post(url, data=data)
    after = time.time()
    print "use %s " % (after-begin)

if __name__ == '__main__':

    pass







