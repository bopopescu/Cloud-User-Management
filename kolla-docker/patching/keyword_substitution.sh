array=("user" "provideraccount" "providervm" "instance" "storagerate" "provider" "providerregion" "instancetype" "usage" "statement" "computerate" "payment" "paymentmethod")

#combine the origin file and the patch file to an empty file
> /root/kolla-docker/patching/zun_compute_api/api.py
cat /root/kolla-docker/patching/zun_compute_api/api_origin.py >> /root/kolla-docker/patching/zun_compute_api/api.py
for i in "${array[@]}"
do
	cat /root/kolla-docker/patching/zun_compute_api/"$i".py >> /root/kolla-docker/patching/zun_compute_api/api.py
done

> /root/kolla-docker/patching/zun_compute_manager/manager.py
cat /root/kolla-docker/patching/zun_compute_manager/manager_origin.py >> /root/kolla-docker/patching/zun_compute_manager/manager.py
for i in "${array[@]}"
do
	cat /root/kolla-docker/patching/zun_compute_manager/"$i".py >> /root/kolla-docker/patching/zun_compute_manager/manager.py
done

> /root/kolla-docker/patching/zun_compute_rpcapi/rpcapi.py
cat /root/kolla-docker/patching/zun_compute_rpcapi/rpcapi_origin.py >> /root/kolla-docker/patching/zun_compute_rpcapi/rpcapi.py
for i in "${array[@]}"
do
	cat /root/kolla-docker/patching/zun_compute_rpcapi/"$i".py >> /root/kolla-docker/patching/zun_compute_rpcapi/rpcapi.py
done

> /root/kolla-docker/patching/zun_db_sqlalchemy_api/api.py
cat /root/kolla-docker/patching/zun_db_sqlalchemy_api/api_origin.py >> /root/kolla-docker/patching/zun_db_sqlalchemy_api/api.py
for i in "${array[@]}"
do
	cat /root/kolla-docker/patching/zun_db_sqlalchemy_api/"$i".py >> /root/kolla-docker/patching/zun_db_sqlalchemy_api/api.py
done

#replace the origin file in kolla-docker project
cp -r /root/kolla-docker/patching/zun_compute_api/api.py /root/kolla-docker/zun/zun/compute/api.py
cp -r /root/kolla-docker/patching/zun_compute_manager/manager.py /root/kolla-docker/zun/zun/compute/manager.py
cp -r /root/kolla-docker/patching/zun_compute_rpcapi/rpcapi.py /root/kolla-docker/zun/zun/compute/rpcapi.py
cp -r /root/kolla-docker/patching/zun_db_sqlalchemy_api/api.py /root/kolla-docker/zun/zun/db/sqlalchemy/api.py
