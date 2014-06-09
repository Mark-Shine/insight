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

class PostRecordForm(forms.Form):
    website = forms.CharField(label=u"用户名")
    message = forms.CharField(label=u"内容")
    title = forms.CharField(label=u"标题")
    time = forms.DateTimeField(label=u"时间",)
    user_name = forms.CharField(label=u'用户名')
    url = forms.URLField(label=u"url")
    ip_and_port = forms.CharField(label=u"ip")
    word = forms.IntegerField(required=False)
    position = forms.CharField(max_length=8, label=u"楼层")
    
