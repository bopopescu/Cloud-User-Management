# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import url

from openstack_auth import utils
from openstack_auth import views

utils.patch_middleware_get_user()


urlpatterns = [
    url(r"^login/$", views.login, name='login'),
    #url('^payments/', include('payments.urls')),

    #url(r"^signup/$", views.signup, name='signup'),
    #url(r"^register/$", views.register, name='register'),
    url(r"^passwordreset/$", views.passwordreset, name='passwordreset'),
    url(r"^signup/$", views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    url(r'^passreset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.passreset, name='passreset'),
    url(r'^pwr/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.pwr, name='pwr'),
    #url(r"^create_user/$", views.create_user, name='create_user'),
    #url(r"^reset_password/$", views.reset_password, name='reset_password'),

    url(r"^logout/$", views.logout, name='logout'),
    url(r'^switch/(?P<tenant_id>[^/]+)/$', views.switch,
        name='switch_tenants'),
    url(r'^switch_services_region/(?P<region_name>[^/]+)/$',
        views.switch_region,
        name='switch_services_region'),
    url(r'^switch_keystone_provider/(?P<keystone_provider>[^/]+)/$',
        views.switch_keystone_provider,
        name='switch_keystone_provider')
]

if utils.is_websso_enabled():
    urlpatterns.append(url(r"^websso/$", views.websso, name='websso'))
