# encoding=utf-8
import json

from django import forms
MAX = 3
MAX_FILES = 5

ZH_ERROR_MSG = {
'required': u'这是必填字段',
'invalid': u'输入内容非法',
'max_length': u"超过最大长度",
}

class AccountForm(forms.Form):
    name = forms.CharField(label=u"用户名")
    email = forms.EmailField(label=u"邮件")
    tel = forms.CharField(label=u"电话")
    password = forms.CharField(label=u"密码",)
    
    
    
    
