#encoding=utf-8
import json
from django.utils import timezone
from django.contrib.auth.hashers import check_password
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
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# Create your views here.
from .models import Account, Team
from .utils import encrypt_password, validate_password

from auth.forms import AccountForm
from monitor.views import BaseView
from monitor.signals import after_action

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        request_context = RequestContext(request, {})
        page = render_to_string(self.template_name, {}, context_instance=request_context)
        return HttpResponse(page)
        
    def post(self, request):
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('home'))
                    # Redirect to a success page.
                else:
                    return HttpResponse("disabled account")
                    # Return a 'disabled account' error message
            else:
                # Return an 'invalid login' error message.
                return HttpResponseRedirect(reverse('login'))
        return HttpResponse("error")


def logoff(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

def delete_account(request, pk):
    owner = request
    user = get_object_or_404(User, id=pk)
    user.delete()
    after_action.send(sender=owner.__class__, 
                user=owner, instance=user, 
                action=u"删除")
    return HttpResponseRedirect(reverse("admin"))


class ChangePasswordView(View):

    template_name = 'change_pw.html'
    def get(self, request):
        page = render_to_string(self.template_name, {}, context_instance=RequestContext(request, {}))
        return HttpResponse(page)
        
    def post(self, request):
        if request.method == "POST":
            data = request.POST
            old = data.get('oldpw')
            new = data.get('newpw')
            comfirm = data.get('comfirmpw')
            user = request.user
            user_id = user.id
            if new != comfirm:
                return HttpResponse(u'两次输入密码不一致')

            user = User.objects.get(id=user_id)
            is_pass = authenticate(username=user.username, password=old)
            if not is_pass:
                return HttpResponse(u"密码错误")
            user.set_password(new)
            user.save()
            return HttpResponseRedirect(reverse("logoff"))
            
        return HttpResponse("error")
    

class AccountAdminView(BaseView):
    template_name = "account_admin.html"    

    def get(self, request):
        self.user = request.user
        context = {}
        context['admin_active'] = 'active'
        page = self.make(request, context)
        return HttpResponse(page)

    def mod_content(self,):
        users_query = Account.objects.filter(team=self.user.account.team)
        page_html = self.include(
            self.template_name, {"accounts":users_query})
        return page_html

    def post(self, request):
        self.user = request.user
        form = AccountForm(request.POST)
        if not form.is_valid():
            return HttpResponse(json.dumps(form._errors))
        cleaned_data = form.cleaned_data
        cleaned_data['password'] = cleaned_data.pop('password1')
        del cleaned_data['password2']
        team = Team.objects.get(id=self.user.account.team.id)
        new_user = User.objects.create_user(**cleaned_data)
        account, created = Account.objects.get_or_create(user=new_user, team=self.user.account.team) 
        after_action.send(sender=account.__class__, 
                user=self.user, instance=account, 
                action=u"添加")
        return HttpResponseRedirect(reverse('admin'))



