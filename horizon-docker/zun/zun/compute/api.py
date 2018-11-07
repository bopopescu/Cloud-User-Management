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

"""Handles all requests relating to compute resources (e.g. containers,
networking and storage of containers, and compute hosts on which they run)."""

# from api_carrier import *
# from api_provider import *

from zun.common import consts
from zun.common import profiler
from zun.compute import rpcapi
from manager import Manager

from zun.scheduler import client as scheduler_client

direct_action=True

@profiler.trace_cls("rpc")
class API(object):
    """API for interacting with the compute manager."""

    def __init__(self, context):
        self.manager = Manager()
        self.rpcapi = rpcapi.API(context=context)
        self.scheduler_client = scheduler_client.SchedulerClient()
        super(API, self).__init__()

    # from api_provider import *

    def user_update(self, context, container, *args):
        if direct_action:
            return self.manager.user_update(context, container, *args)
        else:
            return self.rpcapi.user_update(context, container, *args)

    def user_show(self, context, container, *args):
        if direct_action:
            return self.manager.user_show(context, container)
        else:
            return self.rpcapi.user_show(context, container)

    def user_create(self, context, new_user, extra_spec,
                         requested_networks):
        host_state = None
        try:
            host_state = {} #self._schedule_container(context, new_user, extra_spec)
        except Exception as exc:
            #new_user.status = consts.ERROR
            #new_user.status_reason = str(exc)
            #new_user.save(context)
            return
        if direct_action:
            self.manager.user_create(context, "", requested_networks, new_user)
        else:
            self.rpcapi.user_create(context, "",new_user, "",requested_networks)
        #self.rpcapi.user_create(context, host_state['host'],
        #                             new_user, host_state['limits'],
        #                             requested_networks)

    def user_delete(self, context, container, *args):
        return self.manager.user_delete(context,container,True)
        #return self.rpcapi.user_delete(context, container, *args)

    def providerregion_update(self, context, container, *args):
        if direct_action:
            return self.manager.providerregion_update(context, container, *args)
        else:
            return self.rpcapi.providerregion_update(context, container, *args)

    def providerregion_show(self, context, container, *args):
        if direct_action:
            return self.manager.providerregion_show(context, container)
        else:
            return self.rpcapi.providerregion_show(context, container)

    def providerregion_create(self, context, new_providerregion, extra_spec,
                         requested_networks):
        host_state = None
        try:
            host_state = {} #self._schedule_container(context, new_providerregion, extra_spec)
        except Exception as exc:
            #new_providerregion.status = consts.ERROR
            #new_providerregion.status_reason = str(exc)
            #new_providerregion.save(context)
            return
        if direct_action:
            self.manager.providerregion_create(context, "", requested_networks, new_providerregion)
        else:
            self.rpcapi.providerregion_create(context, "",new_providerregion, "",requested_networks)
        #self.rpcapi.providerregion_create(context, host_state['host'],
        #                             new_providerregion, host_state['limits'],
        #                             requested_networks)

    def providerregion_delete(self, context, container, *args):
        return self.manager.providerregion_delete(context,container,True)
        #return self.rpcapi.providerregion_delete(context, container, *args)



    def carrier_update(self, context, container, *args):
        if direct_action:
            return self.manager.carrier_update(context, container, *args)
        else:
            return self.rpcapi.carrier_update(context, container, *args)

    def carrier_show(self, context, container, *args):
        if direct_action:
            return self.manager.carrier_show(context, container)
        else:
            return self.rpcapi.carrier_show(context, container)

    def carrier_create(self, context, new_carrier, extra_spec,
                         requested_networks):
        host_state = None
        try:
            host_state = {} #self._schedule_container(context, new_carrier, extra_spec)
        except Exception as exc:
            #new_carrier.status = consts.ERROR
            #new_carrier.status_reason = str(exc)
            #new_carrier.save(context)
            return
        if direct_action:
            self.manager.carrier_create(context, "", requested_networks, new_carrier)
        else:
            self.rpcapi.carrier_create(context, "",new_carrier, "",requested_networks)
        #self.rpcapi.carrier_create(context, host_state['host'],
        #                             new_carrier, host_state['limits'],
        #                             requested_networks)

    def carrier_delete(self, context, container, *args):
        return self.manager.carrier_delete(context,container,True)
        #return self.rpcapi.carrier_delete(context, container, *args)

    def container_create(self, context, new_container, extra_spec,
                         requested_networks):
        host_state = None
        try:
            host_state = self._schedule_container(context, new_container,
                                                  extra_spec)
        except Exception as exc:
            new_container.status = consts.ERROR
            new_container.status_reason = str(exc)
            new_container.save(context)
            return

        self.rpcapi.container_create(context, host_state['host'],
                                     new_container, host_state['limits'],
                                     requested_networks)

    def container_run(self, context, new_container, extra_spec,
                      requested_networks):
        host_state = None
        try:
            host_state = self._schedule_container(context, new_container,
                                                  extra_spec)
        except Exception as exc:
            new_container.status = consts.ERROR
            new_container.status_reason = str(exc)
            new_container.save(context)
            return

        self.rpcapi.container_run(context, host_state['host'], new_container,
                                  host_state['limits'], requested_networks)

    def _schedule_container(self, context, new_container, extra_spec):
        dests = self.scheduler_client.select_destinations(context,
                                                          [new_container],
                                                          extra_spec)
        return dests[0]

    def container_delete(self, context, container, *args):
        return self.rpcapi.container_delete(context, container, *args)

    def container_show(self, context, container, *args):
        return self.rpcapi.container_show(context, container, *args)

    def container_reboot(self, context, container, *args):
        return self.rpcapi.container_reboot(context, container, *args)

    def container_stop(self, context, container, *args):
        return self.rpcapi.container_stop(context, container, *args)

    def container_start(self, context, container):
        return self.rpcapi.container_start(context, container)

    def container_pause(self, context, container):
        return self.rpcapi.container_pause(context, container)

    def container_unpause(self, context, container):
        return self.rpcapi.container_unpause(context, container)

    def container_logs(self, context, container, stdout, stderr,
                       timestamps, tail, since):
        return self.rpcapi.container_logs(context, container, stdout, stderr,
                                          timestamps, tail, since)

    def container_exec(self, context, container, *args):
        return self.rpcapi.container_exec(context, container, *args)

    def container_exec_resize(self, context, container, *args):
        return self.rpcapi.container_exec_resize(context, container, *args)

    def container_kill(self, context, container, *args):
        return self.rpcapi.container_kill(context, container, *args)

    def container_update(self, context, container, *args):
        return self.rpcapi.container_update(context, container, *args)

    def container_attach(self, context, container, *args):
        return self.rpcapi.container_attach(context, container, *args)

    def container_resize(self, context, container, *args):
        return self.rpcapi.container_resize(context, container, *args)

    def container_top(self, context, container, *args):
        return self.rpcapi.container_top(context, container, *args)

    def container_get_archive(self, context, container, *args):
        return self.rpcapi.container_get_archive(context, container, *args)

    def add_security_group(self, context, container, *args):
        return self.rpcapi.add_security_group(context, container, *args)

    def container_put_archive(self, context, container, *args):
        return self.rpcapi.container_put_archive(context, container, *args)

    def container_stats(self, context, container):
        return self.rpcapi.container_stats(context, container)

    def container_commit(self, context, container, *args):
        return self.rpcapi.container_commit(context, container, *args)

    def image_pull(self, context, image):
        return self.rpcapi.image_pull(context, image)

    def image_search(self, context, image, image_driver, *args):
        return self.rpcapi.image_search(context, image, image_driver, *args)

    def capsule_create(self, context, new_capsule,
                       requested_networks=None, extra_spec=None):
        host_state = None
        try:
            host_state = self._schedule_container(context, new_capsule,
                                                  extra_spec)
        except Exception as exc:
            new_capsule.status = consts.ERROR
            new_capsule.status_reason = str(exc)
            new_capsule.save(context)
            return
        self.rpcapi.capsule_create(context, host_state['host'], new_capsule,
                                   requested_networks, host_state['limits'])

    def network_detach(self, context, container, *args):
        return self.rpcapi.network_detach(context, container, *args)
    def provider_update(self, context, container, *args):
        if direct_action:
	    return self.manager.provider_update(context, container, *args)
        else:
	    return self.rpcapi.provider_update(context, container, *args)


    def provider_show(self, context, container, *args):
        if direct_action:
	    return self.manager.provider_show(context, container)
        else:
	    return self.rpcapi.provider_show(context, container)


    def provider_create(self, context, new_provider, extra_spec,
		     requested_networks):
        host_state = None
        try:
	    host_state = {}  # self._schedule_container(context, new_provider, extra_spec)
        except Exception as exc:
	    # new_provider.status = consts.ERROR
	    # new_provider.status_reason = str(exc)
	    # new_provider.save(context)
	    return
        if direct_action:
	    self.manager.provider_create(context, "", requested_networks, new_provider)
        else:
	    self.rpcapi.provider_create(context, "", new_provider, "", requested_networks)
        # self.rpcapi.provider_create(context, host_state['host'],
        #                             new_provider, host_state['limits'],
        #                             requested_networks)


    def provider_delete(self, context, container, *args):
        return self.manager.provider_delete(context, container, True)
        # return self.rpcapi.provider_delete(context, container, *args)
