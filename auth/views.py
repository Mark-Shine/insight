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

# Create your views here.
from .models import Account

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        page = render_to_string(self.template_name, {}, context_instance={})
        return HttpResponse(page)
        
    def post(self, request):

        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password')
            user_query = Account.objects.filter(email=email, password=password)
            if user_query:
                user= user_query[0]
                request.session[user.id] = user
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponseRedirect(reverse('login'))



def loginoff(request):
    user = request.user
    try:
        del request.session[user["id"]]
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
        page = render_to_string(self.template_name, {}, context_instance={})
        return HttpResponse(page)
        
    def post(self, request):
        pass
        # if request.method == "POST":
        #     email = request.POST.get('email')
        #     password = request.POST.get('password')
        #     user_query = Account.objects.filter(email=email, password=password)
        #     if user_query:
        #         user= user_query[0]
        #         request.session[user.id] = user
        #         return HttpResponseRedirect(reverse('home'))
        #     else:
        #         return HttpResponseRedirect(reverse('login'))






