
#your_date='DOCKER_OPTS="--insecure-registry docker1.eternova.com:4000"'
#sed -i "s/^#DOCKER_OPTS=.*/${your_date}/" /home/nova/shiyan
echo 'DOCKER_OPTS="--insecure-registry docker1.eternova.com:4000"' >> /etc/default/docker
#if grep -Fxq 'DOCKER_OPTS="--insecure-registry docker1.eternova.com:4000"' /etc/default/docker
#then

#else
        #sed -i '/DOCKER_OPTS=/aDOCKER_OPTS="--insecure-registry docker1.eternova.com:4000"' /etc/default/docker
#fi


cp /lib/systemd/system/docker.service /etc/systemd/system/docker.service


#sed -i.bak '4i\
#This is the new line\
#' /home/nova/shiyan
#sed '/LimitNOFILE=/a \  new line' /home/nova/shiyan
#awk '/LimitNOFILE=/ { print; print "MountFlags=shared"; next }1' /home/nova/shiyan
#awk '/MountFlags=shared/ { print; print "EnvironmentFile=-/etc/default/docker"; next }1' /home/nova/shiyan
#awk '/EnvironmentFile=/ { print; print "ExecStart="; next }1' /home/nova/shiyan
#awk '/ExecStart=/ { print; print "ExecStart=/usr/bin/dockerd -H fd:// $DOCKER_OPTS"; next }1' /home/nova/shiyan
#sed '/LimitNOFILE=/a some text here' /home/nova/shiyan
#sed '/Install/ i MountFlags=shared' /home/nova/shiyan

sed -i '/LimitNOFILE=/aMountFlags=shared' /etc/systemd/system/docker.service
sed -i '/MountFlags=shared/aEnvironmentFile=-/etc/default/docker' /etc/systemd/system/docker.service


sed -i '/ExecStart=/d' /etc/systemd/system/docker.service
sed -i '/EnvironmentFile=/aExecStart=/usr/bin/dockerd -H fd:// $DOCKER_OPTS' /etc/systemd/system/docker.service



systemctl daemon-reload
systemctl restart docker
