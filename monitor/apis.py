#encoding=utf-8
import requests
import httplib, urllib
import time

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


@csrf_exempt
def recieve_data(request):
    raw = request.POST
    data = urllib.unquote(raw).decode('utf8')
    try:
        #获取许可的站点
        sites = Sites.objects.all().values_list('host', flat=True)
        request_ip = request.META['REMOTE_ADDR']
        if request_ip not in sites:
            print "ip not allowed"
            return HttpResponse('not allowed')
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







