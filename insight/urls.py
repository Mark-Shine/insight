#encoding=utf-8
from django.conf.urls import patterns, include, url
from monitor.views import HomeView
from monitor.views import RecordViews
from monitor.views import WordsView
from monitor.apis import recieve_data
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^test$', recieve_data, name="test"),
    url(r'^records$', RecordViews.as_view(), name="records"),
    url(r'^words', include('monitor.urls')),
    # url(r'^insight/', include('insight.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
