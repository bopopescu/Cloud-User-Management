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
# nova-manage cell_v2 simple_cell_setup
nova-manage cell_v2 map_cell0
nova-manage cell_v2 create_cell --name=cell1 --verbose

nova-manage db sync
nova-manage api_db sync
nova-manage db online_data_migrations

# add a second round. for whatever reason, first one can not synch service.uuid in cell0 table
nova-manage db sync
nova-manage api_db sync
nova-manage db online_data_migrations

nova-manage cell_v2 discover_hosts

# stop here in case we need to do it again.
# /bin/bash -c "trap : TERM INT; sleep infinity & wait"
# while true
# do
#  sleep 20
#  nova-manage cell_v2 discover_hosts
# done
