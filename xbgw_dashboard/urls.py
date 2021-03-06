#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2014 Digi International Inc., All Rights Reserved.
#

from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout_then_login
from django.views.generic.base import TemplateView
from rest_framework import routers
from xbgw_dashboard.apps.dashboard import views
from xbgw_dashboard.libs.digi.forms import DeviceCloudAuthenticationForm
from socketio import sdjango

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

# Autodiscover socketio endpoints
sdjango.autodiscover()

# Rest Framework router
dash_api_router = routers.SimpleRouter(trailing_slash=False)
dash_api_router.register(r'user', views.UserViewSet,
                         base_name='deviceclouduser')
dash_api_router.register(r'dashboards', views.DashboardsViewSet,
                         base_name='dashboard')


# Replace REST Framework's login (default django auth form) with our own form
# that has extra fields
rest_api_patterns = patterns(
    'django.contrib.auth.views',
    url(r'^login$', 'login',
        {
            'template_name': 'rest_framework/login.html',
            'authentication_form': DeviceCloudAuthenticationForm
        }, name='login'),
    url(r'^logout$', 'logout',
        {
            'template_name': 'rest_framework/login.html'
        }, name='logout'),
)


urlpatterns = patterns(
    '',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    #(r'^dashboard/', include('apps.dashboard.urls')),
    url(r'^logout$', logout_then_login, name='logout'),
)

# Dashboard Non-API Views
urlpatterns += patterns(
    'xbgw_dashboard.apps.dashboard.views',
    url(r'^$', TemplateView.as_view(template_name='index.html'),
        name="dashboard"),
    # DEBUG
    #url(r'^debug$', 'placeholder', name='dashboard-view'),
    #url(r'^sockettest$', 'socket_test'),
)

# Dashboard API Views not already registered with the router
dashboard_api_patterns = patterns(
    'xbgw_dashboard.apps.dashboard.views',
    url(r'^$', 'api_root'),
    url(r'^login$', 'login_user', name='api_login'),
    url(r'^logout$', 'logout_user', name='api_logout'),
    # Push monitor APIs
    url(r'^monitor$', 'monitor_receiver', name='monitor_receiver'),
    url(r'^monitor/setup/devicecore', 'monitor_devicecore_setup',
        name='monitor_setup_devicecore'),
    url(r'^monitor/setup/(?P<device_id>[0-9A-F\-]+)$', 'monitor_setup',
        name='monitor_setup'),
    # Gateway details and configuration
    url(r'^devices$', views.DevicesList.as_view(), name='devices-list'),
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)$', views.DevicesDetail.as_view(),
        name='devices-detail'),
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/config$',
        views.GatewayConfig.as_view(), name='device-config'),
    # Data streams
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/data$',
        views.DevicesDatastreamList.as_view(), name='device-datastream-list'),
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/data/(?P<stream_id>.+)$',
        views.DevicesDatapointList.as_view(), name='device-datapoint-list'),
    # XBee details, configuration and communications
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/xbees$',
        views.XBeeList.as_view(), name='device-xbee-list'),
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/xbees/(?P<radio>[0-9A-F:]+)/config$',
        views.XBeeConfig.as_view(), name='xbee-config'),
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/xbees/(?P<radio>[0-9A-F:]+)/config-stock$',
        views.XBeeStockConfig.as_view(), name='xbee-stock-config'),
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/io$', views.XBGWDeviceIO.as_view(),
        name='device-io'),
    url(r'^devices/(?P<device_id>[0-9A-F\-]+)/serial$',
        views.XBGWDeviceSerial.as_view(), name='device-serial'),
    url(r'^xbees$', views.XBeeExplicitList.as_view(), name='xbee-list'),
    url(r'^', include(dash_api_router.urls))
)

# Rest Framework
urlpatterns += patterns(
    '',
    url("^socket\.io", include(sdjango.urls)),
    url(r'^api/', include(dashboard_api_patterns)),
    url(r'^api-browser-auth/', include(rest_api_patterns,
        namespace='rest_framework')),
)
