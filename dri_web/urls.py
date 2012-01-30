from django.conf.urls.defaults import patterns, include
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from frontend import views, device_views, router_views, mobile, policy_views

urlpatterns = patterns('',
    (r'^login/$', views.login_get),
    (r'^authenticate/$', views.login_post),
    (r'^dojango/', include('dojango.urls')),
    (r'^$', views.index),

    (r'^known_devices/$', device_views.get_known_devices),
    (r'^device/(?P<mac_address>.*)$', device_views.device),
    (r'^enable_device/$', device_views.enable_device),

    (r'^m$', mobile.index),

    (r'^arp_upload/$', router_views.arp_upload),
    (r'^arp_upload/(?P<filename>.*)$', router_views.arp_upload),
    (r'^iptables_download/$', router_views.iptables_download),

    (r'^policies/$', policy_views.get_policies),
    (r'^traffic_policy/(?P<traffic_policy_name>.*)$', policy_views.edit_traffic_policy),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
