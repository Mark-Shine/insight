# -*- coding: utf-8 *-*
from django.conf.urls import patterns, url

from monitor import views


urlpatterns = patterns(
    'monitor.views',
    url(r'^$', views.WordsView.as_view(), name="words"),
    url(r'^/detail/(?P<pk>\d+)$', views.Word2Record.as_view(), name='word2recod'),
    url(r'^/add$', 'add_word', name='add_word'),
    url(r'^/edit/(?P<pk>\d+)$', 'edit_word', name='edit_word',),
    url(r'^/delete/(?P<pk>\d+)$', 'delete_word', name='delete_word'),
    url(r'^contact$', views.ContactView.as_view(), name="contacts"),
    url(r'^contact/add$', views.ContactView.as_view(), name='add_contact'),
    url(r'^contact/delete/(?P<pk>\d+)$', 'delete_contact', name='delete_contact'),
    url(r'^search/word$', views.SearchWord.as_view(), name="search_word"),
    url(r'^search/record$', views.SearchRecord.as_view(), name="search_record"),
    url(r'^acrecord$', views.AcRecordView.as_view(), name="ac_record"),
    url(r'^acrecord/(?P<pk>\d+)$$', views.AcRecordView.as_view(), name="ac_record"),
    url(r'list/(?P<pk>\d+)', views.WordsView.as_view(), name="words_list"),
    # (r'^(?P<pk>\d+)/edit$', views.EditDemandView.as_view()),
    # (r'^delete$', views.DeleteDemandView.as_view()),
)
