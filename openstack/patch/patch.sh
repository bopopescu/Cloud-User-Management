#!/bin/bash
set -vx
cp ./files/_local_settings.tpl ../openstack-helm/horizon/templates/etc/_local_settings.tpl
cp ./files/_neutron-openvswitch-agent-init.sh.tpl ../openstack-helm/neutron/templates/bin/_neutron-openvswitch-agent-init.sh.tpl
cp ./files/_cell-setup.sh.tpl ../openstack-helm/nova/templates/bin/_cell-setup.sh.tpl
