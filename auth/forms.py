# encoding=utf-8
import json

from django import forms
from django.contrib.auth.forms import UserCreationForm
MAX = 3
MAX_FILES = 5

ZH_ERROR_MSG = {
'required': u'这是必填字段',
'invalid': u'输入内容非法',
'max_length': u"超过最大长度",
}

class AccountForm(UserCreationForm):
    username = forms.CharField(label=u"用户名")
    email = forms.EmailField(label=u"邮件")
    
    
    
    
