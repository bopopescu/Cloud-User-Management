# Copyright 2013 UnitedStack Inc.
# All Rights Reserved.
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

from oslo_log import log as logging
from oslo_utils import strutils
from oslo_utils import uuidutils
import pecan
import six

from zun.api.controllers import base
from zun.api.controllers import link
from zun.api.controllers.v1 import collection
from zun.api.controllers.v1.schemas import containers as schema
from zun.api.controllers.v1.views import users_view as view
from zun.api.controllers import versions
from zun.api import utils as api_utils
from zun.common import consts
from zun.common import exception
from zun.common.i18n import _
from zun.common import name_generator
from zun.common import policy
from zun.common import utils
from zun.common import validation
import zun.conf
from zun.network import neutron
from zun import objects

CONF = zun.conf.CONF
LOG = logging.getLogger(__name__)
NETWORK_ATTACH_EXTERNAL = 'network:attach_external_network'


def _get_container(container_id):
    container = api_utils.get_resource('User', container_id)
    if not container:
        pecan.abort(404, ('Not found; the container you requested '
                          'does not exist.'))

    return container


def check_policy_on_container(container, action):
    context = pecan.request.context
    policy.enforce(context, action, container, action=action)


def is_all_tenants(search_opts):
    all_tenants = search_opts.get('all_tenants')
    if all_tenants:
        try:
            all_tenants = strutils.bool_from_string(all_tenants, True)
        except ValueError as err:
            raise exception.InvalidValue(six.text_type(err))
    else:
        all_tenants = False
    return all_tenants


class ContainerCollection(collection.Collection):
    """API representation of a collection of containers."""

    fields = {
        'users',
        'next'
    }

    """A list containing containers objects"""

    def __init__(self, **kwargs):
        super(ContainerCollection, self).__init__(**kwargs)
        self._type = 'users'

    @staticmethod
    def convert_with_links(rpc_containers, limit, url=None,
                           expand=False, **kwargs):
        collection = ContainerCollection()
        collection.users = \
            [view.format_container(url, p) for p in rpc_containers]
        collection.next = collection.get_next(limit, url=url, **kwargs)
        return collection


class ContainersController(base.Controller):
    """Controller for Containers."""

    _custom_actions = {
        'rename': ['POST'],
        'attach': ['GET'],
        'resize': ['POST'],
        'top': ['GET'],
        'get_archive': ['GET'],
        'put_archive': ['POST'],
        'stats': ['GET'],
        'commit': ['POST'],
        'add_security_group': ['POST'],
        'network_detach': ['POST']
    }

    @pecan.expose('json')
    @exception.wrap_pecan_controller_exception
    def get_all(self, **kwargs):
        """Retrieve a list of containers.

        """
        LOG.debug('user get_all xxx kwargs=%s', kwargs)
        context = pecan.request.context
        policy.enforce(context, "user:get_all",
                       action="user:get_all")
        return self._get_containers_collection(**kwargs)

    def _get_containers_collection(self, **kwargs):
        context = pecan.request.context
        LOG.debug('xxx _get_containers_collection started')
        if is_all_tenants(kwargs):
            LOG.debug('xxx _get_containers_collection true kwargs=%s', kwargs)
            policy.enforce(context, "user:get_all_all_tenants",
                           action="user:get_all_all_tenants")
            context.all_tenants = True
        compute_api = pecan.request.compute_api
        limit = api_utils.validate_limit(kwargs.get('limit'))
        sort_dir = api_utils.validate_sort_dir(kwargs.get('sort_dir', 'asc'))
        sort_key = kwargs.get('sort_key', 'id')
        resource_url = kwargs.get('resource_url')
        expand = kwargs.get('expand')

        filters = None
        marker_obj = None
        marker = kwargs.get('marker')
        if marker:
            marker_obj = objects.Container.get_by_uuid(context,
                                                       marker)
        containers = objects.User.list(context,
                                            limit,
                                            marker_obj,
                                            sort_key,
                                            sort_dir,
                                            filters=filters)
        xx=ContainerCollection.convert_with_links(containers, limit,
                                                      url=resource_url,
                                                      expand=expand,
                                                      sort_key=sort_key,
                                                      sort_dir=sort_dir)
        #LOG.debug('container post xxx containers=%s, xx=%s', containers, xx.__dict__)
        return xx

    @pecan.expose('json')
    @exception.wrap_pecan_controller_exception
    def get_one(self, container_id, **kwargs):
        """Retrieve information about the given container.

        :param container_ident: UUID or name of a container.
        """
        LOG.debug('user get_one xxx container_id=%s, kwargs=%s', container_id, kwargs)
        context = pecan.request.context
        if is_all_tenants(kwargs):
            policy.enforce(context, "user:get_one_all_tenants",
                           action="user:get_one_all_tenants")
            context.all_tenants = True
        container = _get_container(container_id)
        check_policy_on_container(container.as_dict(), "user:get_one")
        compute_api = pecan.request.compute_api
        container = compute_api.user_show(context, container)
        LOG.debug('user get_one xxx host_url=%s, dict=%s', pecan.request.host_url, container.__dict__)
        return view.format_container(pecan.request.host_url, container)

    def _generate_name_for_container(self):
        """Generate a random name like: zeta-22-container."""
        name_gen = name_generator.NameGenerator()
        name = name_gen.generate()
        return name + '-container'


    @pecan.expose('json')
    @api_utils.enforce_content_types(['application/json'])
    @exception.wrap_pecan_controller_exception
    #@validation.validate_query_param(pecan.request, schema.query_param_create)
    #@validation.validated(schema.container_create)
    def post(self, run=False, **container_dict):
        """Create a new container.

        :param run: if true, starts the container
        :param container_dict: a container within the request body.
        """
        LOG.debug('user post xxx run=%s, container_dict=%s', run, container_dict)
        context = pecan.request.context
        compute_api = pecan.request.compute_api
        #LOG.debug('container py post xxx context=%s,compute_api=%s' % (context.to_dict(),dir(compute_api)))
        policy.enforce(context, "user:create",
                       action="user:create")

        requested_networks = {}
        extra_spec = container_dict.get('hints', None)
        new_user = objects.User(context, **container_dict)
        new_user.create(context)
        compute_api.user_create(context, new_user, extra_spec,
                                         requested_networks)
        # Set the HTTP Location Header
        pecan.response.location = link.build_url('users',
                                                     new_user.uuid)
        pecan.response.status = 202
        LOG.debug('user post xxx pecan.response.status=%s', pecan.response.status)
        return view.format_container(pecan.request.host_url, new_user)

    @pecan.expose('json')
    @exception.wrap_pecan_controller_exception
 # disable validation #   @validation.validated(schema.user_update)
    def patch(self, container_id, **patch):
        """Update an existing container.

        :param patch: a json PATCH document to apply to this container.
        """
        container = _get_container(container_id)
        check_policy_on_container(container.as_dict(), "user:update")
       #utils.validate_container_state(container, 'update')
        context = pecan.request.context
        compute_api = pecan.request.compute_api
        container = compute_api.user_update(context, container, patch)
        return view.format_container(pecan.request.host_url, container)

    @pecan.expose('json')
    @exception.wrap_pecan_controller_exception
    @validation.validate_query_param(pecan.request, schema.query_param_rename)
    def rename(self, container_id, name):
        """rename an existing container.

        :param patch: a json PATCH document to apply to this container.
        """
        container = _get_container(container_id)
        check_policy_on_container(container.as_dict(), "user:rename")
        if container.name == name:
            raise exception.Conflict('The new name for the container is the '
                                     'same as the old name.')
        container.name = name
        context = pecan.request.context
        container.save(context)
        return view.format_container(pecan.request.host_url, container)

    @base.Controller.api_version("1.1", "1.6")
    @pecan.expose('json')
    @exception.wrap_pecan_controller_exception
    @validation.validate_query_param(pecan.request, schema.query_param_delete)
    def delete(self, container_id, force=False, **kwargs):
        """Delete a container.

        :param container_ident: UUID or Name of a container.
        """
        LOG.debug('v 1.1 -1.6 User delete xxx container_id=%s, kwargs=%s', container_id, kwargs)
        context = pecan.request.context
        if is_all_tenants(kwargs):
            policy.enforce(context, "user:delete_all_tenants",
                           action="user:delete_all_tenants")
            context.all_tenants = True
        container = _get_container(container_id)
        check_policy_on_container(container.as_dict(), "user:delete")
        try:
            force = strutils.bool_from_string(force, strict=True)
        except ValueError:
            msg = _('Valid force values are true, false, 0, 1, yes and no')
            raise exception.InvalidValue(msg)
        compute_api = pecan.request.compute_api
        compute_api.user_delete(context, container, force)
        pecan.response.status = 204

    @base.Controller.api_version("1.7")  # noqa
    @pecan.expose('json')
    @exception.wrap_pecan_controller_exception
    @validation.validate_query_param(pecan.request, schema.query_param_delete)
    def delete(self, container_id, force=False, **kwargs):
        """Delete a container.

        :param container_ident: UUID or Name of a container.
        """
        LOG.debug('v 1.7 User delete xxx container_id=%s, kwargs=%s', container_id, kwargs)
        context = pecan.request.context
        if is_all_tenants(kwargs):
            policy.enforce(context, "user:delete_all_tenants",
                           action="user:delete_all_tenants")
            context.all_tenants = True
        container = _get_container(container_id)
        check_policy_on_container(container.as_dict(), "user:delete")
        try:
            force = strutils.bool_from_string(force, strict=True)
        except ValueError:
            msg = _('Valid force values are true, false, 0, 1, yes and no')
            raise exception.InvalidValue(msg)
        if not force:
            utils.validate_container_state(container, 'delete')
        else:
            utils.validate_container_state(container, 'delete_force')
            policy.enforce(context, "user:delete_force",
                           action="user:delete_force")
        compute_api = pecan.request.compute_api
        compute_api.user_delete(context, container, force)
        pecan.response.status = 204
