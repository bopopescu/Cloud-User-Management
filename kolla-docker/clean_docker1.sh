#!/bin/bash
#Remove images in docker1.eternova.com registry if changes are made to newly built images

#tag="$(curl http://localhost:4000/v2/eternova/ubuntu-source-horizon/tags/list)" #show tag of the image

#curl -v --silent -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X GET http://localhost:4000/v2/eternova/ubuntu-source-horizon/manifests/pike 2>&1 | grep Docker-Content-Digest | awk '{print ($3)}'

str="$(curl -v --silent -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X GET http://localhost:4000/v2/eternova/ubuntu-source-horizon/manifests/pike 2>&1 | grep Docker-Content-Digest | awk '{print ($3)}')"
#str="sha256:e7c92f22f70e6be05cee3310bb60e9db52938b7846d53023871e3ba6f31bd3bb"
#echo "output1=" $str

#echo "$str" | tr '[\r]' '[~]'
str="$(echo "$str" | tr -d '\r')"
#echo "$str" | tr '[\r]' '[~]'
#str+="xxxxwwwww"
#echo "$str"
#curl http://localhost:4000/v2/eternova/ubuntu-source-horizon/manifests/${str}

curl -v --silent -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X DELETE http://localhost:4000/v2/eternova/ubuntu-source-horizon/manifests/"$str"

did="$(docker ps |grep registry | awk '{print ($1)}')" #show the registry docker ID

docker exec -it "$did" bin/registry garbage-collect  /etc/docker/registry/config.yml #delete the images in registry

#str1="$(curl -v --silent -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X GET http://localhost:4000/v2/eternova/ubuntu-source-horizon/manifests/pike 2>&1 | grep Docker-Content-Digest | awk '{print ($0)}')"
#echo output2="$str1"
#echo output3="http://localhost:4000/v2/eternova/ubuntu-source-hori zon/manifests/"${str}""
#curl -v --silent -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X DELETE http://localhost:4000/v2/eternova/ubuntu-source-horizon/manifests/"${str}"
#echo "http://localhost:4000/v2/eternova/ubuntu-source-horizon/manifests/"${str}""

iid="$(docker images |grep horizon | awk '{print ($3)}')" #show docker images ID
#echo $iid
docker rmi $iid

#Then rebuild the horzion images that have been modified
