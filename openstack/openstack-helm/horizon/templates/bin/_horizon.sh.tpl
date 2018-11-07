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
COMMAND="${@:-start}"

SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
ENABLE_ZUN="yes"
FORCE_GENERATE="no"

function update_sourcefile {

    #pip install django-payments

    git clone http://mr.qinlichao%40hotmail.com:241l69h302S@54.158.21.135/roamercloud/kolla-docker.git /tmp/horizon-zun/

    #cp -rf /tmp/horizon-zun/horizon/payments/* /var/lib/kolla/venv/lib/python2.7/site-packages/payments/

    #cp -rf /tmp/horizon-zun/django-payments/payments/* /var/lib/kolla/venv/lib/python2.7/site-packages/payments/

    cp -rf /tmp/horizon-zun/zun-ui/zun_ui/* /var/lib/kolla/venv/lib/python2.7/site-packages/zun_ui/

    cp -rf /tmp/horizon-zun/python-zunclient/zunclient/* /var/lib/kolla/venv/lib/python2.7/site-packages/zunclient/

    cp -rf /tmp/horizon-zun/zun-ui/zun_ui/* /plugins/zun-ui/zun_ui/

    cp -rf /tmp/horizon-zun/horizon/horizon/* /var/lib/kolla/venv/lib/python2.7/site-packages/horizon/
    cp -rf /tmp/horizon-zun/horizon/openstack_auth/* /var/lib/kolla/venv/lib/python2.7/site-packages/openstack_auth/
    cp -rf /tmp/horizon-zun/horizon/openstack_dashboard/* /var/lib/kolla/venv/lib/python2.7/site-packages/openstack_dashboard/


#    cp -rf /tmp/horizon-zun/zun-ui/zun_ui/static/dashboard/* /var/www/html/horizon/dashboard/
}

function config_dashboard {
    ENABLE=$1
    SRC=$2
    DEST=$3
    if [[ ! -f ${SRC} ]]; then
        echo "WARNING: ${SRC} is required"
    elif [[ "${ENABLE}" == "yes" ]] && [[ ! -f "${DEST}" ]]; then
        cp -a "${SRC}" "${DEST}"
        FORCE_GENERATE="yes"
    elif [[ "${ENABLE}" != "yes" ]] && [[ -f "${DEST}" ]]; then
        # remove pyc pyo files too
        rm -f "${DEST}" "${DEST}c" "${DEST}o"
        FORCE_GENERATE="yes"
    fi
}

function config_zun_dashboard {
    # SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
    for file in ${SITE_PACKAGES}/zun_ui/enabled/_*[^__].py; do
        config_dashboard "${ENABLE_ZUN}" \
            "${SITE_PACKAGES}/zun_ui/enabled/${file##*/}" \
            "${SITE_PACKAGES}/openstack_dashboard/local/enabled/${file##*/}"
    done
}

function start () {
  SITE_PACKAGES_ROOT=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
  rm -f ${SITE_PACKAGES_ROOT}/openstack_dashboard/local/local_settings.py
  ln -s /etc/openstack-dashboard/local_settings ${SITE_PACKAGES_ROOT}/openstack_dashboard/local/local_settings.py

  # wsgi/horizon-http needs open files here, including secret_key_store
  chown -R horizon ${SITE_PACKAGES_ROOT}/openstack_dashboard/local/

  mkdir -p /var/log/kolla/horizon
  chmod 755 /var/log/kolla/horizon
  mkdir -p /var/log/kolla/zun
  chmod 755 /var/log/kolla/zun

  update_sourcefile
  config_zun_dashboard

  if [ -f /etc/apache2/envvars ]; then
     # Loading Apache2 ENV variables
     source /etc/apache2/envvars
  fi
  rm -rf /var/run/apache2/*
  APACHE_DIR="apache2"

  # Compress Horizon's assets.
  /tmp/manage.py collectstatic --noinput
  /tmp/manage.py compress --force
  rm -rf /tmp/_tmp_.secret_key_store.lock /tmp/.secret_key_store
  
  #update_sourcefile

  exec apache2 -DFOREGROUND
  #exec top -b
}

function stop () {
  apachectl -k graceful-stop
}

$COMMAND
