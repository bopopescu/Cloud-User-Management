#!/bin/bash
set -x
FUNC_DIR=/root/devstack
source ${FUNC_DIR}/functions-common
source ${FUNC_DIR}/inc/ini-config
source ${FUNC_DIR}/inc/python
source ${FUNC_DIR}/inc/rootwrap

# create the zun conf directory
ZUN_CONF_DIR=/etc/zun
ZUN_CONF=$ZUN_CONF_DIR/zun.conf
sudo mkdir -p $ZUN_CONF_DIR
sudo chown -R ${USER} $ZUN_CONF_DIR

# generate sample config file and modify it as necessary
sudo chown -R ${USER} .
#tox -egenconfig
sudo cp zun.conf.sample $ZUN_CONF_DIR/zun.conf
sudo cp etc/zun/api-paste.ini $ZUN_CONF_DIR/api-paste.ini

# copy policy.json
sudo cp etc/zun/policy.json $ZUN_CONF_DIR/policy.json

# enable debugging output
sudo sed -i "s/#debug\s*=.*/debug=true/" $ZUN_CONF

# set RabbitMQ userid
sudo sed -i "s/#rabbit_userid\s*=.*/rabbit_userid=zun/" \
         $ZUN_CONF

# set RabbitMQ password
sudo sed -i "s/#rabbit_password\s*=.*/rabbit_password=db2eebbcc7602ba8ca985ad821c3875768436811/" \
         $ZUN_CONF

# set RabbitMQ rabbit_host
sudo sed -i "s/#rabbit_host\s*=.*/rabbit_host=10.254.254.146/" \
         $ZUN_CONF

# set RabbitMQ rabbit_port
sudo sed -i "s/#rabbit_port\s*=.*/rabbit_port=5671/" \
         $ZUN_CONF

# set RabbitMQ rabbit_virtual_host
sudo sed -i "s/#rabbit_virtual_host\s*=.*/rabbit_virtual_host=\/zun/" \
         $ZUN_CONF

# set RabbitMQ rabbit_login_method
sudo sed -i "s/#rabbit_login_method\s*=.*/rabbit_login_method=AMQPLAIN/" \
         $ZUN_CONF

# set SQLAlchemy connection string to connect to MySQL
sudo sed -i "s/#connection\s*=.*/connection=mysql:\/\/root:3a090f3fde2a9a93beee57a0ec8f34d17f327b@10.254.249.2\/zun/" \
         $ZUN_CONF

# set keystone_auth
source /root/openrc admin admin
iniset $ZUN_CONF keystone_auth auth_type password
iniset $ZUN_CONF keystone_auth username zun
iniset $ZUN_CONF keystone_auth password password
iniset $ZUN_CONF keystone_auth project_name service
iniset $ZUN_CONF keystone_auth project_domain_id default
iniset $ZUN_CONF keystone_auth user_domain_id default
iniset $ZUN_CONF keystone_auth auth_url ${OS_AUTH_URL/v2.0/v3}

# NOTE: keystone_authtoken section is deprecated and will be removed.
iniset $ZUN_CONF keystone_authtoken username zun
iniset $ZUN_CONF keystone_authtoken password password
iniset $ZUN_CONF keystone_authtoken project_name service
iniset $ZUN_CONF keystone_authtoken auth_url ${OS_AUTH_URL/v2.0/v3}
iniset $ZUN_CONF keystone_authtoken auth_uri ${OS_AUTH_URL/v2.0/v3}
iniset $ZUN_CONF keystone_authtoken auth_version v3
iniset $ZUN_CONF keystone_authtoken auth_type password
iniset $ZUN_CONF keystone_authtoken user_domain_id default
iniset $ZUN_CONF keystone_authtoken project_domain_id default

