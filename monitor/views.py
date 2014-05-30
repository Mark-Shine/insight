#encoding=utf-8
import time
import json
import datetime
import urllib
from collections import OrderedDict

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
from django.contrib.auth.models import User

from monitor.templatetags.ref import RefNode
from monitor.models import Words
from monitor.models import AlarmRecord
from auth.models import Account, Team
from auth.forms import AccountForm
from auth.utils import encrypt_password
from tracking.views import dashboard
from tracking.models import Visitor, Pageview
from .utils import paginate, page
from tracking.models import WhiteList
from .messages import do_sendmail
from .models import Sites, Contact


class ViewObject(View):
    """
    support utility for collect js,css ref,
    link mods
    """
    tag_html_template = {
        'js': '<script src="%s"></script>',
        'css': '<link rel="stylesheet" href="%s">',
        }

    def __init__(self, **kwargs):
        self.ref_nodes = []
        self.context = Context({})

    def include(self, template_name, context=None):
        template = loader.get_template(template_name)
        self.append_ref(template)
        request_context = self.request_context
        if context:
            request_context.update(context)
        rendered = template.render(request_context)
        if context:
            request_context.pop()
        return rendered


    def mods(self):
        return dict(mod_content="")
        
    def append_ref(self, template):
        self.ref_nodes += template.nodelist.get_nodes_by_type(RefNode)

    def process_static(self, refs, context):
        """
        处理静态文件
        """
        def make_real_ref(r_type, ref_list, params):
            """
            资源url中变量替换,
            放在 标签里面
            ref_list 不是list 而是 js 或者 css的ordereddict,value 都是 None
            """
            for p_ in params:
                for k in ref_list.iterkeys():
                    ref_list[k] = k.replace(
                        '{{%s}}' % p_,
                        context[p_])
            for k_ in ref_list.iterkeys():
                ref_list[k_] = self.tag_html_template[r_type] % ref_list[k_]
        ref_dict = {
            'js': OrderedDict(),
            'css': OrderedDict(),
            }
        for r_ in refs:
            ref_dict[r_.ext][r_.ref_str] = None
        for r_type in ref_dict.keys():
            make_real_ref(
                r_type,
                ref_dict[r_type],
                ['CONTEXT_PATH', 'STATIC_URL'])
        css_tags = ''.join(ref_dict['css'].values())
        js_tags = ''.join(ref_dict['js'].values())
        return (css_tags, js_tags)

    def config(self, request, context=None):
        """配置 include 必须的参数 request_context """
        request_context = RequestContext(request, {})
        for c in self.context.dicts:
            request_context.update(c)
        if context:
            request_context.update(context)
        self.request_context = request_context

    def make(self, request, context=None, **kwargs):
        """
        context: 必须是django.template.context.RequestContext
        template_name 是装配 各种include, mod 的图纸,所以叫(所以叫按照template)make
        """
        self.config(request, context)
        root_template = loader.get_template(self.root_template_name)
        self.append_ref(root_template)
        request_context = self.request_context
        for mod_name, mod_html in self.mods().items():
            request_context[mod_name] = mark_safe(mod_html)
        css_tag, js_tag = self.process_static(self.ref_nodes, self.request_context)
        request_context["css_set"] = mark_safe(css_tag)
        request_context["js_set"] = mark_safe(js_tag)
        return root_template.render(request_context)


class BaseView(ViewObject):

    root_template_name = 'base.html'

    def mods(self):
        """根模板需要的模块"""  
        context = {}
        return dict(
            mod_content=self.mod_content(),)

    def mod_content(self):
        return ""

    def get_words(self, request):
        user = request.user
        words = []
        if user.is_superuser:
            words =  Words.objects.filter(enabled=True,)
        else:
            team = user.account.team
            team_query = Team.objects.get(id=team.id)
            words = team_query.words.filter(enabled=True)
        return words

# Create your views here.
class WordsView(BaseView):
    template_name = 'words.html'

    def mod_content(self, ): 
        words = self.get_words(self.request)
        for w in words:
            w.count = AlarmRecord.objects.filter(word=w.id).count()

        context = {}
        context['words_active'] = 'active'
        context['words'] = words
        page_html = self.include(self.template_name, context)
        return page_html

    def get(self, request, ):
        context = {}
        self.request = request
        page = self.make(request, context)
        return HttpResponse(page)


def add_word(request,):
    if request.method == 'POST':
        word = request.POST.get('word')
        if user.is_superuser:
            return HttpResponse(u"请切换到普通用户")
        team = user.account.team
        new_word = Words.objects.create(**{"word": word})
        Team.objects.create(**{'word':new_word, "team": team})
    return HttpResponseRedirect(reverse("words"))

def edit_word(request, pk):
    pass


def delete_word(request, pk):
    word = get_object_or_404(Words, id=pk)
    word.enabled = False
    word.save()
    return HttpResponseRedirect(reverse("words"))



class HomeView(BaseView):
    template_name = 'home.html'

    def mod_content(self, ):
        page_html = self.include(
            self.template_name, {})
        return page_html

    def get(self, request):
        context = {}
        context['home_active'] = 'active'
        
        page = self.make(request, context)
        return HttpResponse(page)



class RecordViews(BaseView):
    template_name = "records.html"

    def mod_content(self, ):
        team_words = self.get_words(self.request).values_list("id", flat=True)
        records = AlarmRecord.objects.filter(word__in=team_words)
        for r in records:
            r.word_name = Words.objects.filter(id=r.word)[0].word
        page_html = self.include(
            self.template_name, {"records": records})
        return page_html

    def get(self, request):
        context = {}
        self.request = request
        context['records_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)


class Word2Record(BaseView):
    template_name = "word2records.html"

    def mod_content(self, ):
        records = AlarmRecord.objects.filter(word=int(self.pk))
        word = Words.objects.filter(id=self.pk)[0].word
        page_html = self.include(
            self.template_name, {"records": records, "word": word})
        return page_html

    def get(self, request, pk):
        context = {}
        self.pk = pk
        context['records_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)



class TrackView(BaseView):    

    def get(self, request):
        context = {}
        context['admin_active'] = 'active'
        self.request = request
        page = self.make(request, context)
        return HttpResponse(page)

    def mod_content(self,):
        page_html = dashboard(self.request)
        return page_html


class PageView(BaseView):
    template_name = "tracking/pageview.html"

    def get_pagination(self, objects):
        """分页"""
        pagenum = int(self.pagenum or 1)
        paged_objects = paginate(objects, pagenum)
        paged_objects.search_url = reverse('pageview')
        pagination = self.include('monitor/pagination.html', {
            'page_count': range(1, int(paged_objects.page_count)+1),
            'objects':paged_objects,
            'next_two': paged_objects.number + 2,
            'next_three':paged_objects.number + 3,
            'prev_two':paged_objects.number -2,
            'loop_times':range(1,6)})
        return paged_objects, pagination

    def get(self, request, pk=None):
        context = {}
        self.user = request.user
        self.pagenum = request.GET.get('page')
        context['track_active'] = 'active'
        self.mode = pk and 'detail' or 'tolist'
        self.request = request
        self.pk = pk
        page = self.make(request, context)
        return HttpResponse(page)

    def detail(self,):
        visitor_query = Visitor.objects.filter(user_id=self.pk).values_list("session_key", flat=True)
        return Pageview.objects.filter(visitor_id__in=visitor_query)

    def tolist(self, ):
        """只返回该组队员的记录"""
        team = self.user.account.team
        accounts = Account.objects.filter(team=team)
        users = [ account.user for account in accounts ]
        visitors = Visitor.objects.filter(user__in=users)
        return Pageview.objects.all().filter(visitor__in=visitors)

    def mod_content(self, ):
        func = getattr(self, self.mode)
        record_query = func()
        paged_objects, pagination = self.get_pagination(record_query)
        context = {}
        page_html = self.include(
            self.template_name, {"record_query": paged_objects,"pagination": pagination})
        return page_html


class IpControlView(BaseView):
    template_name = 'monitor/ip_control_view.html'

    def get(self, request):
        context = {}
        context['ip_control_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)

    def mod_content(self, ):
        ips = WhiteList.objects.all()
        page_html = self.include(
            self.template_name, {"ips": ips})
        return page_html


def add_ip(request, ):
    if request.method == 'POST':
        ip_str = request.POST.get('ip_str')
        WhiteList.objects.create(**{"ip_address": ip_str})
    return HttpResponseRedirect(reverse("whitelist"))

def delete_ip(request, pk):
    ip_query = get_object_or_404(WhiteList, id=pk)
    ip_query.delete()
    return HttpResponseRedirect(reverse("whitelist"))


def sendmail(request):
    do_sendmail()
    return HttpResponse("hello")


class SitesView(BaseView):
    """监控站点的添加及浏览"""
    
    template_name = "monitor/sites.html"

    def get(self, request):
        context = {}
        context['sites_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)

    def mod_content(self, ):
        sites = Sites.objects.all()
        page_html = self.include(
            self.template_name, {"sites": sites})
        return page_html

    def post(self, request):

        if request.method == 'POST':
            host = request.POST.get('host')
            name = request.POST.get('name')
            Sites.objects.create(**{"host":host, "name":name})
        return HttpResponseRedirect(reverse("sites"))

def delete_site(request, pk):
    """删除监控的站点"""
    sites = get_object_or_404(Sites, id=pk)
    sites.delete()
    return HttpResponseRedirect(reverse("sites"))


class ContactView(BaseView):
    """联系人"""
    
    template_name = "monitor/contacts.html"

    def get(self, request):
        context = {}
        context['contacts_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)

    def mod_content(self, ):
        contacts = Contact.objects.all()
        page_html = self.include(
            self.template_name, {"contacts": contacts})
        return page_html

    def post(self, request):
        if request.method == 'POST':
            phone = request.POST.get('phone')
            name = request.POST.get('name')
            email = request.POST.get('email')
            Contact.objects.create(**{"phone": phone, "name": name, "email": email})
        return HttpResponseRedirect(reverse("contacts"))

def delete_contact(request, pk):
    """删除联系人"""
    contacts = get_object_or_404(Contact, id=pk)
    contacts.delete()
    return HttpResponseRedirect(reverse("contacts"))




