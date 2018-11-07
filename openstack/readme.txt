1. add zun chart
# mkdir /root/openstack/openstack-helm/zun
# cp -r  /root/openstack/openstack-helm/glance/* /root/openstack/openstack-helm/zun

cd /root/openstack/openstack-helm/zun

find . -type f -exec sed -i 's/Glance/Zun/g' {} \;

find . -type f -exec sed -i 's/glance/zun/g' {} \;

https://stackoverflow.com/questions/4793892/recursively-rename-files-using-find-and-sed

find . -name "*glance*" | sed -e "p;s/glance/zun/" | xargs -n2 mv

# update config name
find . -type f -exec sed -i 's/zun-api\.conf/zun\.conf/g' {} \;

