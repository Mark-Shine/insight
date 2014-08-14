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
from django.db.models.signals import post_save

from monitor.templatetags.ref import RefNode
from monitor.models import Words
from monitor.models import AlarmRecord
from monitor.models import Team
from auth.models import Account
from auth.forms import AccountForm
from auth.utils import encrypt_password
from tracking.views import dashboard
from tracking.models import Visitor, Pageview
from .utils import paginate, page
from tracking.models import WhiteList
from .messages import do_sendmail
from .models import Sites, Contact
from monitor.signals import after_action
from monitor.models import ActionRecord


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
            words =  Words.objects.select_related().filter(enabled=True,).order_by("-time")
        else:
            team = user.account.team
            words = Words.objects.select_related().filter(team__id=team.id).order_by("-time")
        return words

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



# Create your views here.
class WordsView(BaseView):
    template_name = 'words.html'

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


    def mod_content(self, ): 
        words = self.get_words(self.request)
        paged_objects, pagination = self.get_pagination(words)
        # for w in paged_objects:
        #     w.count = AlarmRecord.objects.select_related().filter(word=w.id).count()
        context = {}
        context['words'] = paged_objects
        context['pagination'] = pagination
        page_html = self.include(self.template_name, context)
        return page_html

    def get(self, request, ):
        context = {}
        self.request = request
        self.pagenum = request.GET.get('page')
        context['words_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)


def add_word(request,):
    user = request.user
    if request.method == 'POST':
        word = request.POST.get('word')
        time = datetime.datetime.now()
        if user.is_superuser:
            return HttpResponse(u"请切换到普通用户")
        team = user.account.team
        try:
            word, created = Words.objects.get_or_create(word=word, defaults={"time": time})
            after_action.send(sender=word.__class__, 
                user=user, instance=word, 
                action=u"添加")
            word.team.add(team)
            word.save()
        except Exception, e:
            raise e

    return HttpResponseRedirect(reverse("words"))

def edit_word(request, pk):
    pass


def delete_word(request, pk):
    user = request.user
    if not user.account.is_admin:
        return HttpResponseRedirect(reverse("words"))
    word = get_object_or_404(Words, id=pk)
    team = user.account.team
    #todo 不能直接覆盖为False,会影响其他队伍的
    word.enabled = False
    word.team.remove(team)
    word.save()
    after_action.send(sender=word.__class__, 
                user=user, instance=word, 
                action=u"删除")
    return HttpResponseRedirect(reverse("words"))


class HomeView(BaseView):
    template_name = 'home.html'

    def mod_content(self, ):
        team_words = self.get_words(self.request).values_list("id", flat=True)
        records = AlarmRecord.objects.filter(word__in=team_words)
        team = self.request.user.account.team
        sites = Sites.objects.filter(team=team) 
        accounts = Account.objects.filter(team=team)
        context = {
            "team_words": team_words,
            "records": records,
            "sites": sites,
            "accounts": accounts,
        }
        page_html = self.include(
            self.template_name, context)
        return page_html

    def get(self, request):
        context = {}
        context['home_active'] = 'active'
        self.request = request
        page = self.make(request, context)
        return HttpResponse(page)


class RecordViews(BaseView):
    template_name = "records.html"

    def mod_content(self, ):
        team_words = self.get_words(self.request).values_list("id", flat=True)
        records = AlarmRecord.objects.select_related().filter(word__in=team_words).order_by("-time",)
        paged_objects, pagination = self.get_pagination(records)
        page_html = self.include(
            self.template_name, {"records": paged_objects, "pagination": pagination})
        return page_html

    def get(self, request):
        context = {}
        self.request = request
        context['records_active'] = 'active'
        self.pagenum = request.GET.get('page')
        page = self.make(request, context)
        return HttpResponse(page)


def change_record_state(request):
    """更新记录状态"""
    next = request.GET.get("next")
    if request.method == "POST":
        user = request.user
        state = request.POST.get('state')
        pk = request.POST.get("pk")
        a_record = AlarmRecord.objects.get(id=pk)
        a_record.state = int(state)
        a_record.save()
        after_action.send(sender=a_record.__class__, 
                user=user, instance=a_record, 
                action=u"处理")

    return HttpResponseRedirect(next)

class Word2Record(BaseView):
    template_name = "word2records.html"

    def mod_content(self, ):
        records = AlarmRecord.objects.select_related().filter(word=int(self.pk)).order_by("-time",)
        paged_objects, pagination = self.get_pagination(records)
        word = Words.objects.filter(id=self.pk)[0].word
        page_html = self.include(
            self.template_name, {"records": paged_objects, "word": word, "pagination": pagination})
        return page_html

    def get(self, request, pk):
        context = {}
        self.pk = pk
        self.pagenum = request.GET.get('page')
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
        user = request.user
        if not user.account.is_admin:
            return HttpResponseRedirect(reverse("whitelist"))
        ip_str = request.POST.get('ip_str')
        white = WhiteList.objects.create(**{"ip_address": ip_str})
        after_action.send(sender=white.__class__, 
                user=user, instance=white, 
                action=u"添加")
    return HttpResponseRedirect(reverse("whitelist"))


def delete_ip(request, pk):
    user = request.user
    if not user.account.is_admin:
        return HttpResponseRedirect(reverse("whitelist"))
    white = get_object_or_404(WhiteList, id=pk)
    white.delete()
    after_action.send(sender=white.__class__, 
                user=user, instance=white, 
                action=u"添加")
    return HttpResponseRedirect(reverse("whitelist"))


def sendmail(request):
    do_sendmail()
    return HttpResponse("hello")

@csrf_exempt
def search(request):
    site_id = request.POST.get('site_id')
    pid = request.POST.get('pid')
    ars = AlarmRecord.objects.filter(site=site_id).filter(pid=pid) if pid else None
    page = render_to_string("monitor/search_result.html", {"records": ars})
    return HttpResponse(page)


class SitesView(BaseView):
    """监控站点的添加及浏览"""
    
    template_name = "monitor/sites.html"

    def get(self, request):
        context = {}
        context['sites_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)

    def mod_content(self, ):
        sites = Sites.objects.filter(team__id=self.request.user.account.team.id)
        page_html = self.include(
            self.template_name, {"sites": sites})
        return page_html

    def post(self, request):

        if request.method == 'POST':
            user = request.user
            if not user.account.is_admin:
                return HttpResponseRedirect(reverse("sites"))
            team = request.user.account.team
            ip = request.POST.get('ip')
            name = request.POST.get('name')
            sites = Sites.objects.create(**{"ip": ip, "name": name})
            sites.team.add(team)
            sites.save()
            after_action.send(sender=sites.__class__, 
                user=user, instance=sites, 
                action=u"添加")

        return HttpResponseRedirect(reverse("sites"))


def delete_site(request, pk):
    """删除监控的站点"""
    user = request.user
    if not user.account.is_admin:
        return HttpResponseRedirect(reverse("sites"))
    sites = get_object_or_404(Sites, id=pk)
    sites.delete()
    after_action.send(sender=sites.__class__, 
                user=user, instance=sites, 
                action=u"删除")
    return HttpResponseRedirect(reverse("sites"))


class ContactView(BaseView):
    """联系人"""
    
    template_name = "monitor/contacts.html"

    def get(self, request):
        context = {}
        self.request = request
        context['contacts_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)

    def mod_content(self, ):
        team = self.request.user.account.team
        contacts = Contact.objects.filter(team=team)
        page_html = self.include(
            self.template_name, {"contacts": contacts})
        return page_html

    def post(self, request):
        if request.method == 'POST':
            user = request.user
            if not user.account.is_admin:
                return HttpResponseRedirect(reverse("contacts"))
            phone = request.POST.get('phone')
            name = request.POST.get('name')
            email = request.POST.get('email')
            team = request.user.account.team
            contact = Contact.objects.create(**{"phone": phone, 
                "name": name, 
                "email": email, 
                "team": team})
            after_action.send(sender=contact.__class__, 
                user=user, instance=contact, 
                action=u"添加")

        return HttpResponseRedirect(reverse("contacts"))


def delete_contact(request, pk):
    """删除联系人"""
    user = request.user
    if not user.account.is_admin:
        return HttpResponseRedirect(reverse("contacts"))
    contacts = get_object_or_404(Contact, id=pk)
    contacts.delete()
    after_action.send(sender=Contact.__class__, 
                user=user, instance=contacts, 
                action=u"删除")
    return HttpResponseRedirect(reverse("contacts"))


class SearchWord(BaseView):
    template_name = 'words.html'


    def get(self, request):
        self.request = request
        self.pagenum = request.GET.get('page')
        context = {}
        context['words_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)
        

    def mod_content(self, ):
        key = self.request.GET.get("key")
        context = {}
        if  key :
            q = Words.objects.filter(word__contains=key)
            paged_objects, pagination = self.get_pagination(q)
            context['words'] = paged_objects
            context['pagination'] = pagination
        page_html = self.include(self.template_name, context)
        return page_html



class SearchRecord(BaseView):
    template_name = 'records.html'
    def parse_date(self, _date):
        if _date:
            date_list = map(lambda x:int(x), _date.split('-'))
            result = datetime.datetime(date_list[0], date_list[1], date_list[2],)
            return result
        return 

    def get(self, request):
        self.request = request
        self.pagenum = request.GET.get('page')
        context = {}
        context['records_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)
        

    def mod_content(self, ):
        key = self.request.GET.get("key")
        begin = self.request.GET.get("begin_time")
        end = self.request.GET.get("end_time")
        state = self.request.GET.get("state")
        format_begin = self.parse_date(begin)
        format_end = self.parse_date(end)
        context = {}
        qs_end = qs_begin = None
        words = Words.objects.filter(word__contains=key).values_list("id", flat=True)
        q = AlarmRecord.objects.filter(word__in=words)
        if state is not None:
            q = q.filter(state=int(state))
        if format_begin and format_end:
            q = q.filter(Q(time__gte=format_begin) & Q(time__lte=format_end))
        elif format_end:
            q = q.filter(Q(time__lte=format_end))
        elif format_begin:
            q = q.filter(Q(time__gte=format_begin))
        q = q.order_by("-time")
        paged_objects, pagination = self.get_pagination(q)
        context['records'] = paged_objects
        context['pagination'] = pagination
        page_html = self.include(self.template_name, context)
        return page_html


class AcRecordView(BaseView):
    template_name = "monitor/actionrecords.html"

    def get(self, request, pk=None):
        context = {}
        self.user = request.user
        self.pagenum = request.GET.get('page')
        context['ac_active'] = 'active'
        self.mode = pk and 'detail' or 'tolist'
        self.request = request
        self.pk = pk
        page = self.make(request, context)
        return HttpResponse(page)

    def detail(self,):
        ac = ActionRecord.objects.select_related().filter(user_id=self.pk).order_by("-time")
        return ac

    def tolist(self, ):
        """只返回该组队员的记录"""
        team = self.user.account.team
        accounts = Account.objects.filter(team=team)
        users = [ account.user for account in accounts ]
        ac = ActionRecord.objects.select_related().filter(user__in=users).order_by("-time")
        return ac

    def mod_content(self, ):
        func = getattr(self, self.mode)
        record_query = func()
        paged_objects, pagination = self.get_pagination(record_query)
        context = {}
        page_html = self.include(
            self.template_name, {"record_query": paged_objects,"pagination": pagination})
        return page_html


