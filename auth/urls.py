#encoding=utf-8
from django.conf.urls import patterns, include, url
from monitor.views import AccountAdminView
from auth.views import ChangePasswordView, delete_account

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^/admin$', AccountAdminView.as_view(), name="admin"),
    url(r'^/admin/add$', AccountAdminView.as_view(), name="add_user"),
    url(r'^/delete/(?P<pk>\d+)$', delete_account, name='delete_account'),
    url(r'^/changpw$', ChangePasswordView.as_view(), name='change_pw'),
    url(r'^tracking/', include('tracking.urls')),
    # url(r'^insight/', include('insight.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += staticfiles_urlpatterns()