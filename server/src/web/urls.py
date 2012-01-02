from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from dri_server.web.frontend import views

urlpatterns = patterns('',
    (r'^dojango/', include('dojango.urls')),
    (r'^$', views.index),
    (r'^known_devices/$', views.known_devices),
    (r'^login/$', views.login_get),
    (r'^authenticate/$', views.login_post),
    (r'^edit_device/(?P<device_name>.*)$', views.edit_device),
    (r'^enable_device/$', views.enable_device),
    (r'^arp_upload/$', views.arp_upload),
    (r'^arp_upload/(?P<filename>.*)$', views.arp_upload),
    (r'^iptables_download/$', views.iptables_download),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
