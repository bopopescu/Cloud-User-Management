#input parameter definination
panelname=$1
lower=${panelname,,}
upper=${lower^}

#copy the patch part and replace with the input keyword argument
cp -r /root/kolla-docker/patching/zun_compute_api/api_patch.py /root/kolla-docker/patching/zun_compute_api/"$lower".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/patching/zun_compute_api/"$lower".py
sed -i "s/provider/$lower/g" /root/kolla-docker/patching/zun_compute_api/"$lower".py

cp -r /root/kolla-docker/patching/zun_compute_manager/manager_patch.py /root/kolla-docker/patching/zun_compute_manager/"$lower".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/patching/zun_compute_manager/"$lower".py
sed -i "s/provider/$lower/g" /root/kolla-docker/patching/zun_compute_manager/"$lower".py

cp -r /root/kolla-docker/patching/zun_compute_rpcapi/rpcapi_patch.py /root/kolla-docker/patching/zun_compute_rpcapi/"$lower".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/patching/zun_compute_rpcapi/"$lower".py
sed -i "s/provider/$lower/g" /root/kolla-docker/patching/zun_compute_rpcapi/"$lower".py

cp -r /root/kolla-docker/patching/zun_db_sqlalchemy_api/api_patch.py /root/kolla-docker/patching/zun_db_sqlalchemy_api/"$lower".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/patching/zun_db_sqlalchemy_api/"$lower".py
sed -i "s/provider/$lower/g" /root/kolla-docker/patching/zun_db_sqlalchemy_api/"$lower".py
