
[DEFAULT]
# Disable stderr logging
# use_stderr = False
# Logs / State
# turn debug on and off
debug = True
# fatal_deprecations = False
# log_dir = /var/log/nova
state_path = {{ .Values.conf.nova.DEFAULT.state_path }}
# rootwrap_config = /etc/nova/rootwrap.conf
# service_down_time = 120
# default_schedule_zone = nova

# Scheduler
cpu_allocation_ratio = {{ .Values.conf.nova.DEFAULT.cpu_allocation_ratio }}
disk_allocation_ratio = {{ .Values.conf.nova.DEFAULT.disk_allocation_ratio }}
ram_allocation_ratio = {{ .Values.conf.nova.DEFAULT.ram_allocation_ratio }}
reserved_host_disk_mb = 0
reserved_host_memory_mb = 2048

# Compute
compute_driver = {{ .Values.conf.nova.DEFAULT.compute_driver }}
#instance_name_template = instance-%08x
instance_name_template = i-%08x
instances_path = /var/lib/nova/instances
allow_resize_to_same_host = {{ .Values.conf.nova.DEFAULT.allow_resize_to_same_host }}
# image_cache_manager_interval = 0
resume_guests_state_on_host_boot = {{ .Values.conf.nova.DEFAULT.resume_guests_state_on_host_boot }}
linuxnet_interface_driver = {{ .Values.conf.nova.DEFAULT.linuxnet_interface_driver }}
# this setting is unnecessary
# use_neutron = {{ .Values.conf.nova.DEFAULT.use_neutron }}

# Api's
# enabled_apis = osapi_compute,metadata

# Rpc all
transport_url = {{ .Values.conf.nova.DEFAULT.transport_url }}
# executor_thread_pool_size = 64
# rpc_response_timeout = 60

# osapi
osapi_compute_listen = {{ .Values.conf.nova.DEFAULT.osapi_compute_listen }}
osapi_compute_listen_port = {{ .Values.conf.nova.DEFAULT.osapi_compute_listen_port }}
osapi_compute_workers = {{ .Values.conf.nova.DEFAULT.osapi_compute_workers }}

# Metadata
# metadata_host = {{ .Values.conf.nova.DEFAULT.metadata_host }}
metadata_port = {{ .Values.conf.nova.DEFAULT.metadata_port }}
metadata_workers = {{ .Values.conf.nova.DEFAULT.metadata_workers }}

# Network
# dhcpbridge_flagfile = /etc/nova/nova.conf
firewall_driver = nova.virt.firewall.NoopFirewallDriver
my_ip = {{ .Values.conf.nova.DEFAULT.my_ip }}
## Vif
libvirt_vif_type = ethernet
vif_plugging_timeout = 10
# vif_plugging_timeout = 30
vif_plugging_is_fatal = False


# Hypervisor
default_ephemeral_format = {{ .Values.conf.nova.DEFAULT.default_ephemeral_format }}


# Configdrive
# force_config_drive = False

# Ceilometer notification configurations

# Notifications

# Cache
[cache]
enabled = true
backend = oslo_cache.memcache_pool
memcache_servers = {{ .Values.conf.nova.cache.memcache_servers }}


# Cinder
[cinder]
catalog_info = volumev3:cinderv3:internalURL
# cross_az_attach = True
# os_region_name = RegionOne


[spice]
# agent_enabled = false
# enabled = false
# Console Url and binds
# html5proxy_base_url = {{ .Values.conf.nova.spice.html5proxy_base_url }}
html5proxy_host = {{ .Values.conf.nova.spice.html5proxy_host }}
server_listen = {{ .Values.conf.nova.spice.server_listen }}
server_proxyclient_address = {{ .Values.conf.nova.spice.server_proxyclient_address }}


[vnc]
enabled = true
novncproxy_base_url = {{ .Values.conf.nova.vnc.novncproxy_base_url }}
novncproxy_host = {{ .Values.conf.nova.vnc.novncproxy_host }}
novncproxy_port = {{ .Values.conf.nova.vnc.novncproxy_port }}
vncserver_listen = {{ .Values.conf.nova.vnc.vncserver_listen }}
vncserver_proxyclient_address = {{ .Values.conf.nova.vnc.vncserver_proxyclient_address }}

# Glance
[glance]
api_servers = {{ .Values.conf.nova.glance.api_servers }}
num_retries = {{ .Values.conf.nova.glance.num_retries }}

# libvirt
#[libvirt]
#connection_uri = {{ .Values.conf.nova.libvirt.connection_uri }}
#disk_cachemodes = {{ .Values.conf.nova.libvirt.disk_cachemodes }}
#hw_disk_discard = {{ .Values.conf.nova.libvirt.hw_disk_discard }}
#images_rbd_ceph_conf = {{ .Values.conf.nova.libvirt.images_rbd_ceph_conf }}
#images_rbd_pool = {{ .Values.conf.nova.libvirt.images_rbd_pool }}
#images_type = {{ .Values.conf.nova.libvirt.images_type }}
#rbd_secret_uuid = {{ .Values.conf.nova.libvirt.rbd_secret_uuid }}
#rbd_user = {{ .Values.conf.nova.libvirt.rbd_user }}
#virt_type = qemu

# Neutron
[neutron]
url = {{ .Values.conf.nova.neutron.url }}
region_name = {{ .Values.conf.nova.neutron.region_name }}
auth_type = {{ .Values.conf.nova.neutron.auth_type }}
default_floating_pool = public
# Keystone client plugin password option
password = {{ .Values.conf.nova.neutron.password }}
# Keystone client plugin username option
username = {{ .Values.conf.nova.neutron.username }}
project_name = {{ .Values.conf.nova.neutron.project_name }}
user_domain_name = {{ .Values.conf.nova.neutron.user_domain_name }}
project_domain_name = {{ .Values.conf.nova.neutron.project_domain_name }}
# Keystone client plugin authentication URL option
auth_url = {{ .Values.conf.nova.neutron.auth_url }}
auth_version = {{ .Values.conf.nova.neutron.auth_version }}
# insecure = False
metadata_proxy_shared_secret = {{ .Values.conf.nova.neutron.metadata_proxy_shared_secret }}
service_metadata_proxy = {{ .Values.conf.nova.neutron.service_metadata_proxy }}

# Placement
[placement]
os_region_name = {{ .Values.conf.nova.placement.os_region_name }}
# os_interface = internal
auth_type = {{ .Values.conf.nova.placement.auth_type }}
password = {{ .Values.conf.nova.placement.password }}
username = {{ .Values.conf.nova.placement.username }}
project_name = {{ .Values.conf.nova.placement.project_name }}
user_domain_name = {{ .Values.conf.nova.placement.user_domain_name }}
project_domain_name = {{ .Values.conf.nova.placement.project_domain_name }}
auth_url = {{ .Values.conf.nova.placement.auth_url }}
# insecure = False
auth_version = {{ .Values.conf.nova.neutron.auth_version }}

[conductor]
workers = {{ .Values.conf.nova.conductor.workers }}


[keystone_authtoken]
# insecure = False
auth_type = {{ .Values.conf.nova.keystone_authtoken.auth_type }}
auth_url = {{ .Values.conf.nova.keystone_authtoken.auth_url }}
auth_uri = {{ .Values.conf.nova.keystone_authtoken.auth_uri }}
project_domain_name = {{ .Values.conf.nova.keystone_authtoken.project_domain_name }}
user_domain_name = {{ .Values.conf.nova.keystone_authtoken.user_domain_name }}
project_name = {{ .Values.conf.nova.keystone_authtoken.project_name }}
username = {{ .Values.conf.nova.keystone_authtoken.username }}
password = {{ .Values.conf.nova.keystone_authtoken.password }}
region_name = {{ .Values.conf.nova.keystone_authtoken.region_name }}
auth_version = {{ .Values.conf.nova.keystone_authtoken.auth_version }}

memcached_servers = {{ .Values.conf.nova.keystone_authtoken.memcached_servers }}

# token_cache_time = 300

# if your memcached server is shared, use these settings to avoid cache poisoning
memcache_security_strategy = {{ .Values.conf.nova.keystone_authtoken.memcache_security_strategy }}
memcache_secret_key = {{ .Values.conf.nova.keystone_authtoken.memcache_secret_key }}

[database]
connection = {{ .Values.conf.nova.database.connection }}
# max_overflow = 10
# max_pool_size = 120
# pool_timeout = 30
max_retries = -1

[api_database]
connection = {{ .Values.conf.nova.api_database.connection }}
# max_overflow = 10
# max_pool_size = 120
# pool_timeout = 30
max_retries = -1

[cell0_database]
connection = {{ .Values.conf.nova.cell0_database.connection }}
# max_overflow = 10
# max_pool_size = 120
# pool_timeout = 30
max_retries = -1

[placement_database]
connection = {{ .Values.conf.nova.placement_database.connection }}
# max_overflow = 10
# max_pool_size = 120
# pool_timeout = 30
max_retries = -1

[oslo_concurrency]
lock_path = {{ .Values.conf.nova.oslo_concurrency.lock_path }}

# [oslo_messaging_rabbit]
# ssl = True
# rpc_conn_pool_size = 30

[oslo_messaging_notifications]
driver = {{ .Values.conf.nova.oslo_messaging_notifications.driver }}

[oslo_middleware]
enable_proxy_headers_parsing = {{ .Values.conf.nova.oslo_middleware.enable_proxy_headers_parsing }}

[oslo_policy]
policy_file = {{ .Values.conf.nova.oslo_policy.policy_file }}

[wsgi]
api_paste_config = {{ .Values.conf.nova.wsgi.api_paste_config }}
# secure_proxy_ssl_header = HTTP_X_FORWARDED_PROTO

# [api]
# auth_strategy = keystone
# enable_instance_password = True
# use_forwarded_for = True

# [scheduler]
# max_attempts = 5
# scheduler_driver = filter_scheduler
# periodic_task_interval = 60
# host_manager = host_manager
# discover_hosts_in_cells_interval = 60

# [filter_scheduler]
# max_instances_per_host = 50
# max_io_ops_per_host = 10
# ram_weight_multiplier = 5.0
# available_filters = nova.scheduler.filters.all_filters
# enabled_filters = RetryFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,AggregateCoreFilter,AggregateDiskFilter
# host_subset_size = 10
# weight_classes = nova.scheduler.weights.all_weighers
# use_baremetal_filters = False
# tracks_instance_changes = True

# [quota]
# cores = 20
# injected_file_content_bytes = 10240
# injected_file_path_length = 255
# injected_files = 5
# instances = 10
# key_pairs = 100
# max_age = 0
# metadata_items = 128
# ram = 51200
# server_group_members = 10
# server_groups = 10

[upgrade_levels]
compute=auto

