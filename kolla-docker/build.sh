#!/bin/bash
tar czvf horizon-pkt.tar.gz horizon
#cd horizon-12.0.3.dev13 && tar czvf ../horizon-pkt.tar.gz . && cd ..
#cd zun-0.2.1.dev10 && tar czvf ../zun-pkt.tar.gz . && cd ..
tar czvf zun-pkt.tar.gz zun
#cd python-zunclient-0.4.1.dev4 && tar czvf ../zun-client-pkt.tar.gz . && cd ..
tar czvf zun-client-pkt.tar.gz python-zunclient
#cd zun-ui-0.2.1.dev3 && tar czvf ../zun-ui-pkt.tar.gz . && cd ..
tar czvf zun-ui-pkt.tar.gz zun-ui
#/root/kolla/.tox/genconfig/bin/kolla-build --config-file=/root/kolla-docker/kolla-build.conf  2>&1 | tee build_horizon.log
#/root/kolla/.tox/genconfig/bin/kolla-build --config-file=/root/kolla-docker/kolla-build.conf

