#encoding=utf-8
from django.conf.urls import patterns, include, url
from monitor.views import HomeView
from monitor.views import RecordViews
from monitor.views import WordsView, TrackView, PageView
from monitor.apis import recieve_data
from auth.views import LoginView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from monitor.views import IpControlView
from monitor.views import add_ip, delete_ip
from monitor.views import sendmail
from monitor.views import SitesView, delete_site
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^login$', LoginView.as_view(), name="login"),
    url(r'^logoff$', 'auth.views.logoff', name='logoff'),
    url(r'^api/test$', recieve_data, name="recieve"),
    url(r'^records$', RecordViews.as_view(), name="records"),
    url(r'^watchsites$', SitesView.as_view(), name="sites"),
    url(r'^watchsites/add$', SitesView.as_view(), name="add_site"),
    url(r'^watchsites/delete/(?P<pk>\d+)$', delete_site, name="delete_site"),
    url(r'^track$', TrackView.as_view(), name="track"),
    url(r'^track/user$', PageView.as_view(), name="pageview"),
    url(r'^track/user/(?P<pk>\d+)$', PageView.as_view(), name="pageview"),
    url(r'^words', include('monitor.urls')),

    # url(r'^insight/', include('insight.foo.urls')),
    url(r'^auth', include('auth.urls')),
    url(r'^whitelist/add$', add_ip, name='add_ip'),
    url(r'^whitelist/delete/(?P<pk>\d+)$', delete_ip, name='delete_ip'),
    url(r'^whitelist$', IpControlView.as_view(), name='whitelist'),
    url(r'^send$', sendmail, name='sendmail'),
    # url(r'^tracking/', include('tracking.urls')),
    # Uncomment the admin/documentationc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += staticfiles_urlpatterns()