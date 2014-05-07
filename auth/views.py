#encoding=utf-8
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
from django.forms.models import model_to_dict
# Create your views here.
from .models import Account
from .utils import encrypt_password, validate_password

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        request_context = RequestContext(request, {})
        page = render_to_string(self.template_name, {}, context_instance=request_context)
        return HttpResponse(page)
        
    def post(self, request):
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')

            user_query = Account.objects.filter(email=email)
            if user_query:
                user= model_to_dict(user_query[0])
                is_pass = validate_password(user['password'], password)
                if not is_pass:
                    return HttpResponseRedirect(reverse('login'))
                request.session['user'] = user
                request.user = user
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponseRedirect(reverse('login'))
        return HttpResponse("error")


def logoff(request):
    user = request.user
    try:
        del request.session["user"]
    except KeyError:
        pass
    return HttpResponseRedirect(reverse('login'))

def delete_account(request, pk):
    account = get_object_or_404(Account, id=pk)
    account.delete()
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
            user_id = user['id']
            if new != comfirm:
                return HttpResponse(u'两次输入密码不一致')
            account = Account.objects.get(id=user_id)
            hashed = account.password
            is_pass = validate_password(hashed, old)
            if not is_pass:
                return HttpResponse(u"密码错误")
            account.password = encrypt_password(new)
            account.save()
            return HttpResponseRedirect(reverse("logoff"))
            
        return HttpResponse("error")
    





