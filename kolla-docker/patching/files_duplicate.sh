panelname=$1
lower=${panelname,,}
upper=${lower^}
allupper=${lower^^}
one=$upper"s" 
two=$lower"s"
view=$lower"s_view"
fields="fields_"$lower
api="api_"$lower
rest_api="rest_api_"$lower
client="client_"$lower

#duplicate the template file and replace the keyword in it
cp -r /root/kolla-docker/zun/zun/objects/provider.py /root/kolla-docker/zun/zun/objects/"$lower".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun/zun/objects/"$lower".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun/zun/objects/"$lower".py

cp -r /root/kolla-docker/python-zunclient/zunclient/v1/providers.py /root/kolla-docker/python-zunclient/zunclient/v1/"$two".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/python-zunclient/zunclient/v1/"$two".py
sed -i "s/provider/$lower/g" /root/kolla-docker/python-zunclient/zunclient/v1/"$two".py

cp -r /root/kolla-docker/zun/zun/api/controllers/v1/schemas/providers.py /root/kolla-docker/zun/zun/api/controllers/v1/schemas/"$two".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun/zun/api/controllers/v1/schemas/"$two".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun/zun/api/controllers/v1/schemas/"$two".py

cp -r /root/kolla-docker/zun/zun/api/controllers/v1/providers.py /root/kolla-docker/zun/zun/api/controllers/v1/"$two".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun/zun/api/controllers/v1/"$two".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun/zun/api/controllers/v1/"$two".py

cp -r /root/kolla-docker/zun/zun/api/controllers/v1/views/providers_view.py /root/kolla-docker/zun/zun/api/controllers/v1/views/"$view".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun/zun/api/controllers/v1/views/"$view".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun/zun/api/controllers/v1/views/"$view".py

cp -r /root/kolla-docker/zun/zun/objects/fields_provider.py /root/kolla-docker/zun/zun/objects/"$fields".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun/zun/objects/"$fields".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun/zun/objects/"$fields".py

cp -r /root/kolla-docker/zun/zun/db/api_provider.py /root/kolla-docker/zun/zun/db/"$api".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun/zun/db/"$api".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun/zun/db/"$api".py

cp -r /root/kolla-docker/zun-ui/zun_ui/api/rest_api_provider.py /root/kolla-docker/zun-ui/zun_ui/api/"$rest_api".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun-ui/zun_ui/api/"$rest_api".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun-ui/zun_ui/api/"$rest_api".py

cp -r /root/kolla-docker/zun-ui/zun_ui/api/client_provider.py /root/kolla-docker/zun-ui/zun_ui/api/"$client".py
sed -i "s/Provider/$upper/g" /root/kolla-docker/zun-ui/zun_ui/api/"$client".py
sed -i "s/provider/$lower/g" /root/kolla-docker/zun-ui/zun_ui/api/"$client".py
sed -i "s/PROVIDER/$allupper/g" /root/kolla-docker/zun-ui/zun_ui/api/"$client".py
