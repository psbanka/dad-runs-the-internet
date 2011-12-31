from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from dri_server.web.frontend import views

urlpatterns = patterns('',
    (r'^dojango/', include('dojango.urls')),
    (r'^$', views.index),
    (r'^my-first-page/$', views.first_page),
    # Examples:
    # url(r'^$', 'dri_web.views.home', name='home'),
    # url(r'^dri_web/', include('dri_web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
