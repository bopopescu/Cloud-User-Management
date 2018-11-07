helm serve &

cd /root/openstack/openstack-helm
make clean
make

helm install --name=mariadb local/mariadb --namespace=nova --set pod.replicas.server=1 -f /root/openstack/patch/override.yaml --debug
helm install --name=memcached local/memcached --namespace=nova  -f /root/openstack/patch/override.yaml --debug
helm install --name=etcd-rabbitmq local/etcd --namespace=nova -f /root/openstack/patch/override.yaml --debug
helm install --name=rabbitmq local/rabbitmq --namespace=nova -f /root/openstack/patch/override.yaml --debug
helm install --name=ingress local/ingress --namespace=nova -f /root/openstack/patch/override.yaml --debug
helm install --name=keystone local/keystone --namespace=nova --set pod.replicas.api=2 -f /root/openstack/patch/override.yaml --debug
helm install --name=heat local/heat --namespace=nova -f /root/openstack/patch/override.yaml --debug
helm install --namespace=nova --name=horizon local/horizon --set network.enable_node_port=true -f /root/openstack/patch/override.yaml --debug

helm install --namespace=nova --name=glance local/glance --set bootstrap.enabled=false --set pod.replicas.api=1 --set pod.replicas.registry=1 --set storage=pvc -f /root/openstack/patch/override.yaml --debug

helm install --name=openvswitch local/openvswitch --namespace=nova -f /root/openstack/patch/override.yaml --debug
helm install --name=libvirt local/libvirt --namespace=nova -f /root/openstack/patch/override.yaml --debug

helm install --namespace=nova --name=nova local/nova \
   --set pod.replicas.api_metadata=1 \
   --set pod.replicas.osapi=1 \
   --set pod.replicas.conductor=1 \
   --set pod.replicas.consoleauth=1 \
   --set pod.replicas.scheduler=1 \
   --set pod.replicas.novncproxy=1 \
   --set conf.nova.libvirt.virt_type=qemu \
   -f /root/openstack/patch/override.yaml --debug

helm install --namespace=nova --name=neutron local/neutron -f /root/openstack/patch/override.yaml --debug

helm install --namespace=nova --name=zun local/zun --set bootstrap.enabled=false --set pod.replicas.api=1 --set pod.replicas.registry=1 --set storage=pvc -f /root/openstack/patch/override.yaml --debug

