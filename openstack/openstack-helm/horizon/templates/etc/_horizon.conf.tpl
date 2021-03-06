{{/*
Copyright 2017 The Openstack-Helm Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/}}

Listen 0.0.0.0:{{ .Values.network.port}}

LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
LogFormat "%{X-Forwarded-For}i %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" proxy

SetEnvIf X-Forwarded-For "^.*\..*\..*\..*" forwarded
CustomLog /var/log/kolla/horizon/horizon-access.log combined env=!forwarded
CustomLog /var/log/kolla/horizon/horizon-access.log proxy env=forwarded

<VirtualHost *:{{ .Values.network.port}}>
    WSGIScriptReloading On
    WSGIDaemonProcess horizon-http processes=5 threads=1 user=horizon group=horizon display-name=%{GROUP} python-path=/var/lib/kolla/venv/lib/python2.7/site-packages
    WSGIProcessGroup horizon-http
    WSGIScriptAlias / /var/www/cgi-bin/horizon/django.wsgi
    WSGIPassAuthorization On

    <Location "/">
        Require all granted
    </Location>

    Alias /static /var/www/html/horizon
    <Location "/static">
        SetHandler None
    </Location>

    <IfVersion >= 2.4>
      ErrorLogFormat "%{cu}t %M"
    </IfVersion>
    ErrorLog /var/log/kolla/horizon/horizon.log

    SetEnvIf X-Forwarded-For "^.*\..*\..*\..*" forwarded
    CustomLog /var/log/kolla/horizon/horizon-access.log combined env=!forwarded
    CustomLog /var/log/kolla/horizon/horizon-access.log proxy env=forwarded
</Virtualhost>