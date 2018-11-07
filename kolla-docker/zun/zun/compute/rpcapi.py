#    Copyright 2016 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools

from zun.api import servicegroup
from zun.common import exception
from zun.common import profiler
from zun.common import rpc_service
import zun.conf
from zun import objects
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


def check_container_host(func):
    """Verify the state of container host"""
    @functools.wraps(func)
    def wrap(self, context, container, *args, **kwargs):
        services = objects.ZunService.list_by_binary(context, 'zun-compute')
        api_servicegroup = servicegroup.ServiceGroup()
        up_hosts = [service.host for service in services
                    if api_servicegroup.service_is_up(service)]
        #if container.host is not None and container.host not in up_hosts:
            #raise exception.ContainerHostNotUp(container=container.uuid,
        #                                       host=container.host)
        return func(self, context, container, *args, **kwargs)
    return wrap


@profiler.trace_cls("rpc")
class API(rpc_service.API):
    """Client side of the container compute rpc API.

    API version history:

        * 1.0 - Initial version.
        * 1.1 - Add image endpoints.
    """

    def __init__(self, transport=None, context=None, topic=None):
        if topic is None:
            zun.conf.CONF.import_opt(
                'topic', 'zun.conf.compute', group='compute')

        super(API, self).__init__(
            transport, context, topic=zun.conf.CONF.compute.topic)

    def container_create(self, context, host, container, limits,
                         requested_networks, requested_volumes, run,
                         pci_requests):
        self._cast(host, 'container_create', limits=limits,
                   requested_networks=requested_networks,
                   requested_volumes=requested_volumes,
                   container=container,
                   run=run,
                   pci_requests=pci_requests)

    @check_container_host
    def container_delete(self, context, container, force):
        return self._cast(container.host, 'container_delete',
                          container=container, force=force)

    @check_container_host
    def container_show(self, context, container):
        return self._call(container.host, 'container_show',
                          container=container)

    def container_reboot(self, context, container, timeout):
        self._cast(container.host, 'container_reboot', container=container,
                   timeout=timeout)

    def container_stop(self, context, container, timeout):
        self._cast(container.host, 'container_stop', container=container,
                   timeout=timeout)

    def container_start(self, context, container):
        self._cast(container.host, 'container_start', container=container)

    def container_pause(self, context, container):
        self._cast(container.host, 'container_pause', container=container)

    def container_unpause(self, context, container):
        self._cast(container.host, 'container_unpause', container=container)

    @check_container_host
    def container_logs(self, context, container, stdout, stderr,
                       timestamps, tail, since):
        return self._call(container.host, 'container_logs',
                          container=container, stdout=stdout, stderr=stderr,
                          timestamps=timestamps, tail=tail, since=since)

    @check_container_host
    def container_exec(self, context, container, command, run, interactive):
        return self._call(container.host, 'container_exec',
                          container=container, command=command, run=run,
                          interactive=interactive)

    @check_container_host
    def container_exec_resize(self, context, container, exec_id, height,
                              width):
        return self._call(container.host, 'container_exec_resize',
                          exec_id=exec_id, height=height, width=width)

    def container_kill(self, context, container, signal):
        self._cast(container.host, 'container_kill', container=container,
                   signal=signal)

    @check_container_host
    def container_update(self, context, container, patch):
        return self._call(container.host, 'container_update',
                          container=container, patch=patch)

    @check_container_host
    def container_attach(self, context, container):
        return self._call(container.host, 'container_attach',
                          container=container)

    @check_container_host
    def container_resize(self, context, container, height, width):
        return self._call(container.host, 'container_resize',
                          container=container, height=height, width=width)

    @check_container_host
    def container_top(self, context, container, ps_args):
        return self._call(container.host, 'container_top',
                          container=container, ps_args=ps_args)

    @check_container_host
    def container_get_archive(self, context, container, path):
        return self._call(container.host, 'container_get_archive',
                          container=container, path=path)

    @check_container_host
    def container_put_archive(self, context, container, path, data):
        return self._call(container.host, 'container_put_archive',
                          container=container, path=path, data=data)

    @check_container_host
    def container_stats(self, context, container):
        return self._call(container.host, 'container_stats',
                          container=container)

    @check_container_host
    def container_commit(self, context, container, repository, tag):
        return self._call(container.host, 'container_commit',
                          container=container, repository=repository, tag=tag)

    def add_security_group(self, context, container, security_group):
        return self._cast(container.host, 'add_security_group',
                          container=container, security_group=security_group)

    def remove_security_group(self, context, container, security_group):
        return self._cast(container.host, 'remove_security_group',
                          container=container, security_group=security_group)

    def image_pull(self, context, image):
        # NOTE(hongbin): Image API doesn't support multiple compute nodes
        # scenario yet, so we temporarily set host to None and rpc will
        # choose an arbitrary host.
        host = None
        self._cast(host, 'image_pull', image=image)

    def image_search(self, context, image, image_driver, exact_match,
                     host=None):
        return self._call(host, 'image_search', image=image,
                          image_driver_name=image_driver,
                          exact_match=exact_match)

    def capsule_create(self, context, host, capsule,
                       requested_networks, requested_volumes, limits):
        self._cast(host, 'capsule_create',
                   capsule=capsule,
                   requested_networks=requested_networks,
                   requested_volumes=requested_volumes,
                   limits=limits)

    def capsule_delete(self, context, capsule):
        return self._call(capsule.host, 'capsule_delete',
                          capsule=capsule)

    def network_detach(self, context, container, network):
        return self._call(container.host, 'network_detach',
                          container=container, network=network)

    def network_attach(self, context, container, network):
        return self._call(container.host, 'network_attach',
                          container=container, network=network)
    def user_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi user_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'user_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def user_delete(self, context, container, force):
        LOG.debug('rpcapi user_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'user_delete',
                          container=container, force=force)

    #@check_container_host
    def user_show(self, context, container):
        return self._call("", 'user_show',
                          container=container)

    #@check_container_host
    def user_update(self, context, container, patch):
        LOG.debug('user_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'user_update',
                          container=container, patch=patch)

    
    def provideraccount_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi provideraccount_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'provideraccount_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def provideraccount_delete(self, context, container, force):
        LOG.debug('rpcapi provideraccount_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'provideraccount_delete',
                          container=container, force=force)

    #@check_container_host
    def provideraccount_show(self, context, container):
        return self._call("", 'provideraccount_show',
                          container=container)

    #@check_container_host
    def provideraccount_update(self, context, container, patch):
        LOG.debug('provideraccount_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'provideraccount_update',
                          container=container, patch=patch)

    
    def providervm_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi providervm_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'providervm_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def providervm_delete(self, context, container, force):
        LOG.debug('rpcapi providervm_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'providervm_delete',
                          container=container, force=force)

    #@check_container_host
    def providervm_show(self, context, container):
        return self._call("", 'providervm_show',
                          container=container)

    #@check_container_host
    def providervm_update(self, context, container, patch):
        LOG.debug('providervm_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'providervm_update',
                          container=container, patch=patch)

    
    def instance_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi instance_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'instance_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def instance_delete(self, context, container, force):
        LOG.debug('rpcapi instance_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'instance_delete',
                          container=container, force=force)

    #@check_container_host
    def instance_show(self, context, container):
        return self._call("", 'instance_show',
                          container=container)

    #@check_container_host
    def instance_update(self, context, container, patch):
        LOG.debug('instance_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'instance_update',
                          container=container, patch=patch)

    
    def storagerate_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi storagerate_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'storagerate_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def storagerate_delete(self, context, container, force):
        LOG.debug('rpcapi storagerate_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'storagerate_delete',
                          container=container, force=force)

    #@check_container_host
    def storagerate_show(self, context, container):
        return self._call("", 'storagerate_show',
                          container=container)

    #@check_container_host
    def storagerate_update(self, context, container, patch):
        LOG.debug('storagerate_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'storagerate_update',
                          container=container, patch=patch)

    
    def provider_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi provider_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'provider_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def provider_delete(self, context, container, force):
        LOG.debug('rpcapi provider_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'provider_delete',
                          container=container, force=force)

    #@check_container_host
    def provider_show(self, context, container):
        return self._call("", 'provider_show',
                          container=container)

    #@check_container_host
    def provider_update(self, context, container, patch):
        LOG.debug('provider_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'provider_update',
                          container=container, patch=patch)

    
    def providerregion_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi providerregion_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'providerregion_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def providerregion_delete(self, context, container, force):
        LOG.debug('rpcapi providerregion_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'providerregion_delete',
                          container=container, force=force)

    #@check_container_host
    def providerregion_show(self, context, container):
        return self._call("", 'providerregion_show',
                          container=container)

    #@check_container_host
    def providerregion_update(self, context, container, patch):
        LOG.debug('providerregion_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'providerregion_update',
                          container=container, patch=patch)

    
    def instancetype_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi instancetype_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'instancetype_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def instancetype_delete(self, context, container, force):
        LOG.debug('rpcapi instancetype_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'instancetype_delete',
                          container=container, force=force)

    #@check_container_host
    def instancetype_show(self, context, container):
        return self._call("", 'instancetype_show',
                          container=container)

    #@check_container_host
    def instancetype_update(self, context, container, patch):
        LOG.debug('instancetype_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'instancetype_update',
                          container=container, patch=patch)

    
    def usage_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi usage_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'usage_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def usage_delete(self, context, container, force):
        LOG.debug('rpcapi usage_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'usage_delete',
                          container=container, force=force)

    #@check_container_host
    def usage_show(self, context, container):
        return self._call("", 'usage_show',
                          container=container)

    #@check_container_host
    def usage_update(self, context, container, patch):
        LOG.debug('usage_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'usage_update',
                          container=container, patch=patch)

    
    def statement_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi statement_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'statement_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def statement_delete(self, context, container, force):
        LOG.debug('rpcapi statement_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'statement_delete',
                          container=container, force=force)

    #@check_container_host
    def statement_show(self, context, container):
        return self._call("", 'statement_show',
                          container=container)

    #@check_container_host
    def statement_update(self, context, container, patch):
        LOG.debug('statement_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'statement_update',
                          container=container, patch=patch)

    
    def computerate_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi computerate_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'computerate_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def computerate_delete(self, context, container, force):
        LOG.debug('rpcapi computerate_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'computerate_delete',
                          container=container, force=force)

    #@check_container_host
    def computerate_show(self, context, container):
        return self._call("", 'computerate_show',
                          container=container)

    #@check_container_host
    def computerate_update(self, context, container, patch):
        LOG.debug('computerate_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'computerate_update',
                          container=container, patch=patch)

    
    def payment_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi payment_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'payment_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def payment_delete(self, context, container, force):
        LOG.debug('rpcapi payment_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'payment_delete',
                          container=container, force=force)

    #@check_container_host
    def payment_show(self, context, container):
        return self._call("", 'payment_show',
                          container=container)

    #@check_container_host
    def payment_update(self, context, container, patch):
        LOG.debug('payment_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'payment_update',
                          container=container, patch=patch)

    
    def paymentmethod_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi paymentmethod_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'paymentmethod_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def paymentmethod_delete(self, context, container, force):
        LOG.debug('rpcapi paymentmethod_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'paymentmethod_delete',
                          container=container, force=force)

    #@check_container_host
    def paymentmethod_show(self, context, container):
        return self._call("", 'paymentmethod_show',
                          container=container)

    #@check_container_host
    def paymentmethod_update(self, context, container, patch):
        LOG.debug('paymentmethod_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'paymentmethod_update',
                          container=container, patch=patch)

    
