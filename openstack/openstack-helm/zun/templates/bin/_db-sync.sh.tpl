#!/bin/bash

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

set -ex
function update_sourcefile {
    git clone http://mr.qinlichao%40hotmail.com:241l69h302S@54.158.21.135/roamercloud/kolla-docker.git /tmp/horizon-zun/
    cp -rf /tmp/horizon-zun/zun/zun/* /var/lib/kolla/venv/lib/python2.7/site-packages/zun/
}

update_sourcefile
zun-db-manage upgrade
zun-db-manage revision --message "add new" --autogenerate
zun-db-manage upgrade
