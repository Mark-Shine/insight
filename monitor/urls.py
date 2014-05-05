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

    # (r'^(?P<pk>\d+)/edit$', views.EditDemandView.as_view()),
    # (r'^delete$', views.DeleteDemandView.as_view()),
)
