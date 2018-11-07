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

from zun.common import consts
from zun.common import exception
from zun.common import profiler
from zun.compute import container_actions
from zun.compute import rpcapi
import zun.conf
from zun import objects
from zun.scheduler import client as scheduler_client
from manager import Manager

CONF = zun.conf.CONF
direct_action=True

@profiler.trace_cls("rpc")
class API(object):
    """API for interacting with the compute manager."""

    def __init__(self, context):
        self.manager = Manager()
        self.rpcapi = rpcapi.API(context=context)
        self.scheduler_client = scheduler_client.SchedulerClient()
        super(API, self).__init__()

    def _record_action_start(self, context, container, action):
        objects.ContainerAction.action_start(context, container.uuid,
                                             action, want_result=False)

    def container_create(self, context, new_container, extra_spec,
                         requested_networks, requested_volumes, run,
                         pci_requests=None):
        host_state = None
        try:
            host_state = self._schedule_container(context, new_container,
                                                  extra_spec)
        except Exception as exc:
            new_container.status = consts.ERROR
            new_container.status_reason = str(exc)
            new_container.save(context)
            return

        # NOTE(mkrai): Intent here is to check the existence of image
        # before proceeding to create container. If image is not found,
        # container create will fail with 400 status.
        if CONF.api.enable_image_validation:
            try:
                images = self.rpcapi.image_search(
                    context, new_container.image,
                    new_container.image_driver, True, host_state['host'])
                if not images:
                    raise exception.ImageNotFound(image=new_container.image)
            except Exception as e:
                new_container.status = consts.ERROR
                new_container.status_reason = str(e)
                new_container.save(context)
                raise

        self._record_action_start(context, new_container,
                                  container_actions.CREATE)
        self.rpcapi.container_create(context, host_state['host'],
                                     new_container, host_state['limits'],
                                     requested_networks, requested_volumes,
                                     run, pci_requests)

    def _schedule_container(self, context, new_container, extra_spec):
        dests = self.scheduler_client.select_destinations(context,
                                                          [new_container],
                                                          extra_spec)
        return dests[0]

    def container_delete(self, context, container, *args):
        self._record_action_start(context, container, container_actions.DELETE)
        return self.rpcapi.container_delete(context, container, *args)

    def container_show(self, context, container, *args):
        return self.rpcapi.container_show(context, container, *args)

    def container_reboot(self, context, container, *args):
        self._record_action_start(context, container, container_actions.REBOOT)
        return self.rpcapi.container_reboot(context, container, *args)

    def container_stop(self, context, container, *args):
        self._record_action_start(context, container, container_actions.STOP)
        return self.rpcapi.container_stop(context, container, *args)

    def container_start(self, context, container):
        self._record_action_start(context, container, container_actions.START)
        return self.rpcapi.container_start(context, container)

    def container_pause(self, context, container):
        self._record_action_start(context, container, container_actions.PAUSE)
        return self.rpcapi.container_pause(context, container)

    def container_unpause(self, context, container):
        self._record_action_start(context, container,
                                  container_actions.UNPAUSE)
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
        self._record_action_start(context, container, container_actions.KILL)
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
        self._record_action_start(context, container,
                                  container_actions.ADD_SECURITY_GROUP)
        return self.rpcapi.add_security_group(context, container, *args)

    def remove_security_group(self, context, container, *args):
        self._record_action_start(context, container,
                                  container_actions.REMOVE_SECURITY_GROUP)
        return self.rpcapi.remove_security_group(context, container, *args)

    def container_put_archive(self, context, container, *args):
        return self.rpcapi.container_put_archive(context, container, *args)

    def container_stats(self, context, container):
        return self.rpcapi.container_stats(context, container)

    def container_commit(self, context, container, *args):
        self._record_action_start(context, container, container_actions.COMMIT)
        return self.rpcapi.container_commit(context, container, *args)

    def image_pull(self, context, image):
        return self.rpcapi.image_pull(context, image)

    def image_search(self, context, image, image_driver, exact_match, *args):
        return self.rpcapi.image_search(context, image, image_driver,
                                        exact_match, *args)

    def capsule_create(self, context, new_capsule, requested_networks=None,
                       requested_volumes=None, extra_spec=None):
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
                                   requested_networks, requested_volumes,
                                   host_state['limits'])

    def capsule_delete(self, context, capsule, *args):
        return self.rpcapi.capsule_delete(context, capsule, *args)

    def network_detach(self, context, container, *args):
        self._record_action_start(context, container,
                                  container_actions.NETWORK_DETACH)
        return self.rpcapi.network_detach(context, container, *args)

    def network_attach(self, context, container, *args):
        self._record_action_start(context, container,
                                  container_actions.NETWORK_ATTACH)
        return self.rpcapi.network_attach(context, container, *args)
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
            host_state = {}  # self._schedule_container(context, new_user, extra_spec)
        except Exception as exc:
            # new_user.status = consts.ERROR
            # new_user.status_reason = str(exc)
            # new_user.save(context)
            return
        if direct_action:
            self.manager.user_create(context, "", requested_networks, new_user)
        else:
            self.rpcapi.user_create(context, "", new_user, "", requested_networks)
        # self.rpcapi.user_create(context, host_state['host'],
        #                             new_user, host_state['limits'],
        #                             requested_networks)


    def user_delete(self, context, container, *args):
        return self.manager.user_delete(context, container, True)
        # return self.rpcapi.user_delete(context, container, *args)
    def provideraccount_update(self, context, container, *args):
        if direct_action:
            return self.manager.provideraccount_update(context, container, *args)
        else:
            return self.rpcapi.provideraccount_update(context, container, *args)


    def provideraccount_show(self, context, container, *args):
        if direct_action:
            return self.manager.provideraccount_show(context, container)
        else:
            return self.rpcapi.provideraccount_show(context, container)


    def provideraccount_create(self, context, new_provideraccount, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_provideraccount, extra_spec)
        except Exception as exc:
            # new_provideraccount.status = consts.ERROR
            # new_provideraccount.status_reason = str(exc)
            # new_provideraccount.save(context)
            return
        if direct_action:
            self.manager.provideraccount_create(context, "", requested_networks, new_provideraccount)
        else:
            self.rpcapi.provideraccount_create(context, "", new_provideraccount, "", requested_networks)
        # self.rpcapi.provideraccount_create(context, host_state['host'],
        #                             new_provideraccount, host_state['limits'],
        #                             requested_networks)


    def provideraccount_delete(self, context, container, *args):
        return self.manager.provideraccount_delete(context, container, True)
        # return self.rpcapi.provideraccount_delete(context, container, *args)
    def providervm_update(self, context, container, *args):
        if direct_action:
            return self.manager.providervm_update(context, container, *args)
        else:
            return self.rpcapi.providervm_update(context, container, *args)


    def providervm_show(self, context, container, *args):
        if direct_action:
            return self.manager.providervm_show(context, container)
        else:
            return self.rpcapi.providervm_show(context, container)


    def providervm_create(self, context, new_providervm, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_providervm, extra_spec)
        except Exception as exc:
            # new_providervm.status = consts.ERROR
            # new_providervm.status_reason = str(exc)
            # new_providervm.save(context)
            return
        if direct_action:
            self.manager.providervm_create(context, "", requested_networks, new_providervm)
        else:
            self.rpcapi.providervm_create(context, "", new_providervm, "", requested_networks)
        # self.rpcapi.providervm_create(context, host_state['host'],
        #                             new_providervm, host_state['limits'],
        #                             requested_networks)


    def providervm_delete(self, context, container, *args):
        return self.manager.providervm_delete(context, container, True)
        # return self.rpcapi.providervm_delete(context, container, *args)
    def instance_update(self, context, container, *args):
        if direct_action:
            return self.manager.instance_update(context, container, *args)
        else:
            return self.rpcapi.instance_update(context, container, *args)


    def instance_show(self, context, container, *args):
        if direct_action:
            return self.manager.instance_show(context, container)
        else:
            return self.rpcapi.instance_show(context, container)


    def instance_create(self, context, new_instance, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_instance, extra_spec)
        except Exception as exc:
            # new_instance.status = consts.ERROR
            # new_instance.status_reason = str(exc)
            # new_instance.save(context)
            return
        if direct_action:
            self.manager.instance_create(context, "", requested_networks, new_instance)
        else:
            self.rpcapi.instance_create(context, "", new_instance, "", requested_networks)
        # self.rpcapi.instance_create(context, host_state['host'],
        #                             new_instance, host_state['limits'],
        #                             requested_networks)


    def instance_delete(self, context, container, *args):
        return self.manager.instance_delete(context, container, True)
        # return self.rpcapi.instance_delete(context, container, *args)
    def storagerate_update(self, context, container, *args):
        if direct_action:
            return self.manager.storagerate_update(context, container, *args)
        else:
            return self.rpcapi.storagerate_update(context, container, *args)


    def storagerate_show(self, context, container, *args):
        if direct_action:
            return self.manager.storagerate_show(context, container)
        else:
            return self.rpcapi.storagerate_show(context, container)


    def storagerate_create(self, context, new_storagerate, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_storagerate, extra_spec)
        except Exception as exc:
            # new_storagerate.status = consts.ERROR
            # new_storagerate.status_reason = str(exc)
            # new_storagerate.save(context)
            return
        if direct_action:
            self.manager.storagerate_create(context, "", requested_networks, new_storagerate)
        else:
            self.rpcapi.storagerate_create(context, "", new_storagerate, "", requested_networks)
        # self.rpcapi.storagerate_create(context, host_state['host'],
        #                             new_storagerate, host_state['limits'],
        #                             requested_networks)


    def storagerate_delete(self, context, container, *args):
        return self.manager.storagerate_delete(context, container, True)
        # return self.rpcapi.storagerate_delete(context, container, *args)
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
            host_state = {}  # self._schedule_container(context, new_providerregion, extra_spec)
        except Exception as exc:
            # new_providerregion.status = consts.ERROR
            # new_providerregion.status_reason = str(exc)
            # new_providerregion.save(context)
            return
        if direct_action:
            self.manager.providerregion_create(context, "", requested_networks, new_providerregion)
        else:
            self.rpcapi.providerregion_create(context, "", new_providerregion, "", requested_networks)
        # self.rpcapi.providerregion_create(context, host_state['host'],
        #                             new_providerregion, host_state['limits'],
        #                             requested_networks)


    def providerregion_delete(self, context, container, *args):
        return self.manager.providerregion_delete(context, container, True)
        # return self.rpcapi.providerregion_delete(context, container, *args)
    def instancetype_update(self, context, container, *args):
        if direct_action:
            return self.manager.instancetype_update(context, container, *args)
        else:
            return self.rpcapi.instancetype_update(context, container, *args)


    def instancetype_show(self, context, container, *args):
        if direct_action:
            return self.manager.instancetype_show(context, container)
        else:
            return self.rpcapi.instancetype_show(context, container)


    def instancetype_create(self, context, new_instancetype, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_instancetype, extra_spec)
        except Exception as exc:
            # new_instancetype.status = consts.ERROR
            # new_instancetype.status_reason = str(exc)
            # new_instancetype.save(context)
            return
        if direct_action:
            self.manager.instancetype_create(context, "", requested_networks, new_instancetype)
        else:
            self.rpcapi.instancetype_create(context, "", new_instancetype, "", requested_networks)
        # self.rpcapi.instancetype_create(context, host_state['host'],
        #                             new_instancetype, host_state['limits'],
        #                             requested_networks)


    def instancetype_delete(self, context, container, *args):
        return self.manager.instancetype_delete(context, container, True)
        # return self.rpcapi.instancetype_delete(context, container, *args)
    def usage_update(self, context, container, *args):
        if direct_action:
            return self.manager.usage_update(context, container, *args)
        else:
            return self.rpcapi.usage_update(context, container, *args)


    def usage_show(self, context, container, *args):
        if direct_action:
            return self.manager.usage_show(context, container)
        else:
            return self.rpcapi.usage_show(context, container)


    def usage_create(self, context, new_usage, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_usage, extra_spec)
        except Exception as exc:
            # new_usage.status = consts.ERROR
            # new_usage.status_reason = str(exc)
            # new_usage.save(context)
            return
        if direct_action:
            self.manager.usage_create(context, "", requested_networks, new_usage)
        else:
            self.rpcapi.usage_create(context, "", new_usage, "", requested_networks)
        # self.rpcapi.usage_create(context, host_state['host'],
        #                             new_usage, host_state['limits'],
        #                             requested_networks)


    def usage_delete(self, context, container, *args):
        return self.manager.usage_delete(context, container, True)
        # return self.rpcapi.usage_delete(context, container, *args)
    def statement_update(self, context, container, *args):
        if direct_action:
            return self.manager.statement_update(context, container, *args)
        else:
            return self.rpcapi.statement_update(context, container, *args)


    def statement_show(self, context, container, *args):
        if direct_action:
            return self.manager.statement_show(context, container)
        else:
            return self.rpcapi.statement_show(context, container)


    def statement_create(self, context, new_statement, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_statement, extra_spec)
        except Exception as exc:
            # new_statement.status = consts.ERROR
            # new_statement.status_reason = str(exc)
            # new_statement.save(context)
            return
        if direct_action:
            self.manager.statement_create(context, "", requested_networks, new_statement)
        else:
            self.rpcapi.statement_create(context, "", new_statement, "", requested_networks)
        # self.rpcapi.statement_create(context, host_state['host'],
        #                             new_statement, host_state['limits'],
        #                             requested_networks)


    def statement_delete(self, context, container, *args):
        return self.manager.statement_delete(context, container, True)
        # return self.rpcapi.statement_delete(context, container, *args)
    def computerate_update(self, context, container, *args):
        if direct_action:
            return self.manager.computerate_update(context, container, *args)
        else:
            return self.rpcapi.computerate_update(context, container, *args)


    def computerate_show(self, context, container, *args):
        if direct_action:
            return self.manager.computerate_show(context, container)
        else:
            return self.rpcapi.computerate_show(context, container)


    def computerate_create(self, context, new_computerate, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_computerate, extra_spec)
        except Exception as exc:
            # new_computerate.status = consts.ERROR
            # new_computerate.status_reason = str(exc)
            # new_computerate.save(context)
            return
        if direct_action:
            self.manager.computerate_create(context, "", requested_networks, new_computerate)
        else:
            self.rpcapi.computerate_create(context, "", new_computerate, "", requested_networks)
        # self.rpcapi.computerate_create(context, host_state['host'],
        #                             new_computerate, host_state['limits'],
        #                             requested_networks)


    def computerate_delete(self, context, container, *args):
        return self.manager.computerate_delete(context, container, True)
        # return self.rpcapi.computerate_delete(context, container, *args)
    def payment_update(self, context, container, *args):
        if direct_action:
            return self.manager.payment_update(context, container, *args)
        else:
            return self.rpcapi.payment_update(context, container, *args)


    def payment_show(self, context, container, *args):
        if direct_action:
            return self.manager.payment_show(context, container)
        else:
            return self.rpcapi.payment_show(context, container)


    def payment_create(self, context, new_payment, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_payment, extra_spec)
        except Exception as exc:
            # new_payment.status = consts.ERROR
            # new_payment.status_reason = str(exc)
            # new_payment.save(context)
            return
        if direct_action:
            self.manager.payment_create(context, "", requested_networks, new_payment)
        else:
            self.rpcapi.payment_create(context, "", new_payment, "", requested_networks)
        # self.rpcapi.payment_create(context, host_state['host'],
        #                             new_payment, host_state['limits'],
        #                             requested_networks)


    def payment_delete(self, context, container, *args):
        return self.manager.payment_delete(context, container, True)
        # return self.rpcapi.payment_delete(context, container, *args)
    def paymentmethod_update(self, context, container, *args):
        if direct_action:
            return self.manager.paymentmethod_update(context, container, *args)
        else:
            return self.rpcapi.paymentmethod_update(context, container, *args)


    def paymentmethod_show(self, context, container, *args):
        if direct_action:
            return self.manager.paymentmethod_show(context, container)
        else:
            return self.rpcapi.paymentmethod_show(context, container)


    def paymentmethod_create(self, context, new_paymentmethod, extra_spec,
                        requested_networks):
        host_state = None
        try:
            host_state = {}  # self._schedule_container(context, new_paymentmethod, extra_spec)
        except Exception as exc:
            # new_paymentmethod.status = consts.ERROR
            # new_paymentmethod.status_reason = str(exc)
            # new_paymentmethod.save(context)
            return
        if direct_action:
            self.manager.paymentmethod_create(context, "", requested_networks, new_paymentmethod)
        else:
            self.rpcapi.paymentmethod_create(context, "", new_paymentmethod, "", requested_networks)
        # self.rpcapi.paymentmethod_create(context, host_state['host'],
        #                             new_paymentmethod, host_state['limits'],
        #                             requested_networks)


    def paymentmethod_delete(self, context, container, *args):
        return self.manager.paymentmethod_delete(context, container, True)
        # return self.rpcapi.paymentmethod_delete(context, container, *args)
