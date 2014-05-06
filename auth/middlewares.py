#coding=utf-8

import httplib
import json
import urllib
import logging
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from auth.utils import user_info
from auth import BBC_HOST
import auth


log = logging.getLogger('exception')


def get_client_ip(request):
    """get user's ip """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# def new_track(request, user):
#     meta = request.META
#     current_url = (meta['wsgi.url_scheme']
#            + "://" + meta['HTTP_HOST'] + request.get_full_path())
#     data = {}
#     data['userId'] = user['staff_id']
#     data['userName'] = user['realname'].encode('utf-8')
#     data['userIp'] = get_client_ip(request)
#     data['userNick'] = (user.get('nickNameCn') or user.get('wangwang')) .encode('utf-8') or ""
#     data['operateValue'] = current_url
#     data['operateKey'] = 'view'
#     data['operateItem'] = 'tuiguang'
#     params = urllib.urlencode(data)
#     urllib.urlopen(TRACK_URL, params)


def get_user(request):
    user = request.session.get('user')
    # if not user:
    #     token = request.COOKIES[USERNAME_COOKIE_KEY]
    #     result = fork(token)
    #     if result.get("status"):
    #         staff_id = result['data']['empId']
    #         user = user_info(staff_id, nocache=1)
    #         if user:
    #             request.session['user'] = user
    #     else:
    #         return None
    return user

def falk_user(request, falk_staff_id):
    """生成模拟用户"""

    real_user = get_user(request)
    #判断其真实用户是否为管理员
    if real_user['staff_id'] in SETTINGS.SUPER_USERS:
        user = user_info(falk_staff_id)
        return user


class AuthenticationMiddleware(object):
    """
        代替django默认的登陆验证,找cookie中的的用户id信息,写入session
        保持和django.contrib.auth注入request对象的行为一致
    """

    def process_request(self, request):
        user = request.session.get('user')
        if not user:
            return HttpResponseRedirect(reverse("login"))
        request.user = user

        # if request.META['PATH_INFO'] in auth.FREE_PATH:
        #     return
        # auth_url = 'http://%s%s/login' % (SETTINGS.HTTP_HOST, CONTEXT_PATH)
        # next_url = ('http://%s%s/'
        #      % (SETTINGS.HTTP_HOST, CONTEXT_PATH))
        #如果是auth返回token，写入cookie
        # token =  request.POST.get('token')
        # back_url = request.POST.get('back_url')
        # if token:
            # res = HttpResponseRedirect(next_url)
            # res.set_cookie(USERNAME_COOKIE_KEY, token)
            # rawdata = fork(token)
            # if rawdata.get("status"):
            #     staff_id = rawdata['data']['empId']
            #     user = user_info(staff_id)
            #     if user:
            #         request.session['user'] = user
            # else:
            #     return None
            # return res
        #没有 token 去ark 获取token
        # if not USERNAME_COOKIE_KEY in request.COOKIES:
        #     return goto_ark(auth_url)
        #支持 以指定用户登陆
        # falk_staff_id = request.GET.get('falk')
        # if falk_staff_id:
        #     user = falk_user(request, falk_staff_id)
        #     if not user:
        #         #去掉url參數獲取路徑
        #         path = request.get_full_path()
        #         loc = path.index('?')
        #         current_path = path[:loc]
        #         return HttpResponseRedirect(current_path)

        # elif getattr(SETTINGS, "TEST_USER", None):
        #     user = user_info(SETTINGS.TEST_USER, nocache=1)
        # else:
        # user = request.session.get('user')
        # # user = get_user(request)
        # if not user:
        #     return HttpResponseRedirect(reverse("login"))
            
            #todo 不要使用debug 作为逻辑判断的标志，副作用太大
            # if not SETTINGS.DEBUG:
            #     try:
            #         new_track(request, user)
            #     except:
            #         log.info('track error,the user is: ')
            #         log.info(user)
            # request.user = user
        # else:

