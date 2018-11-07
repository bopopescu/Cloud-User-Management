[DEFAULT]
debug = {{ .Values.conf.zun.api.zun_logging_debug }}

log_file = /var/log/kolla/zun/zun-api.log

log_dir = /var/log/kolla/zun
transport_url = {{ .Values.conf.zun.DEFAULT.transport_url }}

state_path = /var/lib/zun
container_driver = docker.driver.DockerDriver
db_type = sql

[network]
driver = kuryr

[api]
host_ip = 0.0.0.0
port = {{ .Values.conf.zun.DEFAULT.bind_port }}
workers = {{ .Values.conf.zun.api.openstack_service_workers }}

[compute]
topic = zun-compute

[database]
connection = {{ .Values.conf.zun.database.connection }}
max_retries = -1


[zun_client]
version = 1
service_type = container
service_name = zun

[keystone_auth]
auth_uri = {{ .Values.conf.zun.keystone_authtoken.auth_uri }}
auth_url = {{ .Values.conf.zun.keystone_authtoken.auth_url }}
auth_type = password
project_domain_id = {{ .Values.conf.zun.keystone_auth.default_project_domain_id }}
user_domain_id = {{ .Values.conf.zun.keystone_auth.default_user_domain_id }}
project_name = service
username = {{ .Values.conf.zun.keystone_auth.zun_keystone_user }}
password = {{ .Values.conf.zun.keystone_auth.zun_keystone_password }}

memcache_security_strategy = ENCRYPT
memcache_secret_key = {{ .Values.conf.zun.keystone_auth.memcache_secret_key }}
memcached_servers = {{ .Values.conf.zun.keystone_authtoken.memcached_servers }}

[keystone_authtoken]
auth_uri = {{ .Values.conf.zun.keystone_authtoken.auth_uri }}
auth_url = {{ .Values.conf.zun.keystone_authtoken.auth_url }}
auth_type = password
project_domain_id = {{ .Values.conf.zun.keystone_authtoken.default_project_domain_id }}
user_domain_id = {{ .Values.conf.zun.keystone_authtoken.default_user_domain_id }}
project_name = service
username = {{ .Values.conf.zun.keystone_authtoken.zun_keystone_user }}
password = {{ .Values.conf.zun.keystone_authtoken.zun_keystone_password }}
service_token_roles_required = True

memcache_security_strategy = ENCRYPT
memcache_secret_key = {{ .Values.conf.zun.keystone_authtoken.memcache_secret_key }}
memcached_servers = {{ .Values.conf.zun.keystone_authtoken.memcached_servers}}

[glance_client]
auth_uri = {{ .Values.conf.zun.keystone_authtoken.auth_uri }}
auth_url = {{ .Values.conf.zun.keystone_authtoken.auth_url }}
auth_type = password
project_domain_id = {{ .Values.conf.zun.glance_client.default_project_domain_id }}
user_domain_id = {{ .Values.conf.zun.glance_client.default_user_domain_id }}
project_name = service
username = {{ .Values.conf.zun.glance_client.zun_keystone_user }}
password = {{ .Values.conf.zun.glance_client.zun_keystone_password }}
region_name = {{ .Values.conf.zun.glance_client.openstack_region_name }}
endpoint_type = internalURL

[neutron_client]
auth_uri = {{ .Values.conf.zun.keystone_authtoken.auth_uri }}
auth_url = {{ .Values.conf.zun.keystone_authtoken.auth_url }}
auth_type = password
project_domain_id = {{ .Values.conf.zun.neutron_client.default_project_domain_id }}
user_domain_id = {{ .Values.conf.zun.neutron_client.default_user_domain_id }}
project_name = service
username = {{ .Values.conf.zun.neutron_client.zun_keystone_user }}
password = {{ .Values.conf.zun.neutron_client.zun_keystone_password }}
region_name = {{ .Values.conf.zun.neutron_client.openstack_region_name }}
endpoint_type = internalURL

[oslo_concurrency]
lock_path = /var/lib/zun/tmp



[profiler]
enabled = false
trace_sqlalchemy = true
hmac_keys = {{ .Values.conf.zun.profiler.osprofiler_secret }}


connection_string = elasticsearch://{{ .Values.conf.zun.profiler.elasticsearch_address }}:{{ .Values.conf.zun.profiler.elasticsearch_port }}


