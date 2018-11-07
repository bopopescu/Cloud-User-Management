#!/bin/bash
/root/kolla/.tox/genconfig/bin/kolla-build --config-file=/root/horizon-docker/kolla-build.conf  2>&1 | tee build_horizon.log
