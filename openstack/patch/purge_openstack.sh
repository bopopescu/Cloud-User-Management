helm del --purge zun
helm del --purge neutron
helm del --purge nova
helm del --purge libvirt
helm del --purge openvswitch
helm del --purge glance
helm del --purge horizon
helm del --purge heat
helm del --purge keystone
helm del --purge ingress
helm del --purge rabbitmq
helm del --purge etcd-rabbitmq
helm del --purge memcached
helm del --purge mariadb


kubectl delete pvc zun-images -n nova
kubectl delete pvc glance-images -n nova
kubectl delete pvc mysql-data-mariadb-1 -n nova
kubectl delete pvc mysql-data-mariadb-0 -n nova
