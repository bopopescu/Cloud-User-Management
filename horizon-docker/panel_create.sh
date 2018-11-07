panelname=$1
four=${panelname,,}
three=${four^}
one=$three"s" 
two=$four"s"

mkdir /root/horizon-docker-backup/zun-ui/zun_ui/content/container/$two/ 
mkdir /root/horizon-docker-backup/zun-ui/zun_ui/static/dashboard/container/$two/

#substitute content part string
cp -r /root/zun-ui-infra/zun_ui/content/container/carriers/* /root/horizon-docker-backup/zun-ui/zun_ui/content/container/$two/
sed -i "s/Carriers/$one/g" /root/horizon-docker-backup/zun-ui/zun_ui/content/container/$two/*
sed -i "s/carriers/$two/g" /root/horizon-docker-backup/zun-ui/zun_ui/content/container/$two/*
sed -i "s/Carrier/$three/g" /root/horizon-docker-backup/zun-ui/zun_ui/content/container/$two/*

#substitute enabled part string, remember to change the new file name manunally!
cp -r /root/zun-ui-infra/zun_ui/enabled/_2332_admin_container_carriers_panel.py /root/horizon-docker-backup/zun-ui/zun_ui/enabled/"$two".py
sed -i "s/Carriers/$one/g" /root/horizon-docker-backup/zun-ui/zun_ui/enabled/"$two".py
sed -i "s/carriers/$two/g" /root/horizon-docker-backup/zun-ui/zun_ui/enabled/"$two".py

#substitute static part string, remember to add one line in the container.module.js!
cp -r /root/zun-ui-infra/zun_ui/static/dashboard/container/carriers/* /root/horizon-docker-backup/zun-ui/zun_ui/static/dashboard/container/$two/
#sed -i "s/Carriers/$one/g" /root/horizon-docker/zun-ui/zun_ui/static/dashboard/container/$two/*
#sed -i "s/carriers/$two/g" /root/horizon-docker/zun-ui/zun_ui/static/dashboard/container/$two/*
#sed -i "s/Carrier/$three/g" /root/horizon-docker/zun-ui/zun_ui/static/dashboard/container/$two/*
#sed -i "s/carrier/$four/g" /root/horizon-docker/zun-ui/zun_ui/static/dashboard/container/$two/*
find /root/horizon-docker-backup/zun-ui/zun_ui/static/dashboard/container/$two/ -exec sed -i "s/Carriers/$one/g" {} \;
find /root/horizon-docker-backup/zun-ui/zun_ui/static/dashboard/container/$two/ -exec sed -i "s/carriers/$two/g" {} \;
find /root/horizon-docker-backup/zun-ui/zun_ui/static/dashboard/container/$two/ -exec sed -i "s/Carrier/$three/g" {} \;
find /root/horizon-docker-backup/zun-ui/zun_ui/static/dashboard/container/$two/ -exec sed -i "s/carrier/$four/g" {} \;

#cp /root/zun-ui-infra/zun_ui/static/dashboard/container/zun.service.js /root/horizon-docker/zun-ui/zun_ui/static/dashboard/container/zun.service.js
