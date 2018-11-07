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

# set -ex
set -x

#service lxd stop

if [ -n "$(cat /proc/*/comm 2>/dev/null | grep -w lxd)" ]; then
    echo "ERROR: lxd daemon already running on host" 1>&2
    #cat /proc/*/comm
    #exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
fi

usermod -G lxd -a nova

/usr/bin/lxd init \
  --auto \
  --network-address={{ .Values.conf.liblxd.lxd_bind_address }} \
  --network-port={{ .Values.conf.liblxd.lxd_bind_port }} \
  --storage-backend={{ .Values.conf.liblxd.lxd_storage_backend }}
#  \
#  --trust-password={{ .Values.conf.liblxd.lxd_trust_password }}
#  --storage-pool={{ .Values.conf.liblxd.lxd_storage_pool }}
cat <<EOF | lxd init --preseed
config:
  core.https_address: 0.0.0.0:8843
networks:
- name: lxdbr0
  type: bridge
  config:
    ipv4.address: auto
    ipv6.address: auto
profiles:
- name: default
  devices:
    eth0:
      nictype: bridged
      parent: lxdbr0
      type: nic
EOF

# lxd init will auto start service
#exec /usr/bin/lxd --group lxd --logfile=/var/log/lxd/lxd.log

service lxd restart

# exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
# instead of using loop, we start our console server
apt update
apt install git -y
git clone http://mr.qinlichao%40hotmail.com:241l69h302S@54.158.21.135/roamercloud/console-server.git /console-server
cd /console-server
./console-server
exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
