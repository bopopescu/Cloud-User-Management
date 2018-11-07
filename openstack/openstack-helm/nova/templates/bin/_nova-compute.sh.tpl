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

set -x

function update_sourcefile {
    git clone http://mr.qinlichao%40hotmail.com:241l69h302S@54.158.21.135/roamercloud/kolla-docker.git /tmp/kolla-docker/
    cp -rf /tmp/kolla-docker/nova/nova/* /var/lib/kolla/venv/lib/python2.7/site-packages/nova/
    # update pylxd to fix container issue
    cp -rf /tmp/kolla-docker/pylxd/pylxd/* /var/lib/kolla/venv/lib/python2.7/site-packages/pylxd/
    #update nova-lxd
    cp -rf /tmp/kolla-docker/nova-lxd/nova/virt/* /var/lib/kolla/venv/lib/python2.7/site-packages/nova/virt/
}

update_sourcefile


cat /etc/nova/nova.conf
# since we do not populate right nova-vnc.ini info, so just remove it. let nova.conf handle the vnc config
# cat /tmp/pod-shared/nova-vnc.ini

console_kind="{{- .Values.console.console_kind -}}"
if [ "${console_kind}" == "novnc" ] ; then
exec nova-compute \
      --config-file /etc/nova/nova.conf \
#      --config-file /tmp/pod-shared/nova-vnc.ini
elif [ "${console_kind}" == "spice" ] ; then
exec nova-compute \
      --config-file /etc/nova/nova.conf \
#      --config-file /tmp/pod-shared/nova-spice.ini
else
exec nova-compute \
      --config-file /etc/nova/nova.conf
fi
exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
