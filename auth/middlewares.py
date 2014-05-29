#coding=utf-8

import httplib
import json
import urllib
import logging
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse



log = logging.getLogger('exception')


def get_client_ip(request):
    """get user's ip """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class AuthenticationMiddleware(object):
    """
        代替django默认的登陆验证,找cookie中的的用户id信息,写入session
        保持和django.contrib.auth注入request对象的行为一致
    """

    def process_request(self, request):
        #exclude login 
        if request.path.startswith("/admin"):
            return None
        if request.path.startswith(reverse('login')):
            return None
        if request.path.startswith(reverse('recieve')):
            return None
        user = request.session.get('user')
        if not user:
            return HttpResponseRedirect(reverse("login"))
        request.user = user


