# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
Base API for Database
"""

from oslo_db import api as db_api

from zun.common import exception
from zun.common.i18n import _
from zun.common import profiler
import zun.conf
import logging
LOG = logging.getLogger(__name__)

"""Add the database backend mapping here"""

CONF = zun.conf.CONF
_BACKEND_MAPPING = {'sqlalchemy': 'zun.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(CONF,
                                backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


@profiler.trace("db")
def _get_dbdriver_instance():
    """Return a DB API instance."""
    return IMPL


@profiler.trace("db")
def list_users(context, filters=None, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
    """List matching users.

    Return a list of the specified columns for all users that match
    the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of users to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_users(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_user(context, values):
    """Create a new user.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the user, and several dicts which are
                   passed
                   into the Drivers when managing this user. For
                   example:
                   ::
                    {
                     'uuid': uuidutils.generate_uuid(),
                     'name': 'example',
                     'type': 'virt'
                    }
    :returns: A user.
    """
    LOG.info("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    LOG.info(context)
    LOG.info(values)
    return _get_dbdriver_instance().create_user(context, values)


@profiler.trace("db")
def get_user_by_uuid(context, user_uuid):
    """Return a user.

    :param context: The security context
    :param user_uuid: The uuid of a user.
    :returns: A user.
    """
    return _get_dbdriver_instance().get_user_by_uuid(
        context, user_uuid)


@profiler.trace("db")
def get_user_by_name(context, user_name):
    """Return a user.

    :param context: The security context
    :param user_name: The name of a user.
    :returns: A user.
    """
    return _get_dbdriver_instance().get_user_by_name(
        context, user_name)


@profiler.trace("db")
def destroy_user(context, user_id):
    """Destroy a user and all associated interfaces.

    :param context: Request context
    :param user_id: The id or uuid of a user.
    """
    return _get_dbdriver_instance().destroy_user(context, user_id)


@profiler.trace("db")
def update_user(context, user_id, values):
    """Update properties of a user.

    :context: Request context
    :param user_id: The id or uuid of a user.
    :values: The properties to be updated
    :returns: A user.
    :raises: ContainerNotFound
    """

    #LOG.info("update_user update_user update_user update_user update_user update_user update_user update_user update_user update_user update_user")
    #LOG.info(context)
    #LOG.info(user_id)
    #LOG.info(values)
    #LOG.info(values['activation_expir_date'])


    '''try:
        date = str(values['activation_expir_date'])
        date = date.split("+")
        values['activation_expir_date'] = date[0]
    except Exception:
        LOG.info("activation_expir_date does not exist")

    try:
        date = str(values['passreset_expir_date'])
        date = date.split("+")
        values['passreset_expir_date'] = date[0]
    except Exception:
        LOG.info("passreset_expir_date does not exist")'''
    #values = {'activation_url': u'http://35.232.192.150:31000/auth/activate/ODNkMTQ2ZTktYTM5My00ZDAxLTg4NWQtNzIzZTdjODk5NDRm/4xs-6da02193a7f6ba5cd507/\n', 'activation_expir_date': datetime.datetime(2018, 7, 18, 16, 5, 13, 464673, tzinfo=<FixedOffset u'+00:00' datetime.timedelta(0)>)}
    #values = {'activation_url': u'http://35.232.192.150:31000/auth/activate/ODNkMTQ2ZTktYTM5My00ZDAxLTg4NWQtNzIzZTdjODk5NDRm/4xs-6da02193a7f6ba5cd507/', 'activation_expir_date': '2018-07-11 14:42:54'}

    process_date("activation_expir_date", values)
    process_date("passreset_expir_date", values)
    process_date("last_login_time", values)
    return _get_dbdriver_instance().update_user(
        context, user_id, values)

def process_date(date_key, values):
    try:
        date = str(values[date_key])
        date = date.split("+")
        values[date_key] = date[0]
    except Exception:
        LOG.info("date_key: " + str(date_key) + "does not exist in values: " + str(values))

@profiler.trace("db")
def list_containers(context, filters=None, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
    """List matching containers.

    Return a list of the specified columns for all containers that match
    the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of containers to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_containers(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_container(context, values):
    """Create a new container.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the container, and several dicts which are
                   passed
                   into the Drivers when managing this container. For
                   example:
                   ::
                    {
                     'uuid': uuidutils.generate_uuid(),
                     'name': 'example',
                     'type': 'virt'
                    }
    :returns: A container.
    """
    return _get_dbdriver_instance().create_container(context, values)


@profiler.trace("db")
def get_container_by_uuid(context, container_uuid):
    """Return a container.

    :param context: The security context
    :param container_uuid: The uuid of a container.
    :returns: A container.
    """
    return _get_dbdriver_instance().get_container_by_uuid(
        context, container_uuid)


@profiler.trace("db")
def get_container_by_name(context, container_name):
    """Return a container.

    :param context: The security context
    :param container_name: The name of a container.
    :returns: A container.
    """
    return _get_dbdriver_instance().get_container_by_name(
        context, container_name)


@profiler.trace("db")
def destroy_container(context, container_id):
    """Destroy a container and all associated interfaces.

    :param context: Request context
    :param container_id: The id or uuid of a container.
    """
    return _get_dbdriver_instance().destroy_container(context, container_id)


@profiler.trace("db")
def update_container(context, container_id, values):
    """Update properties of a container.

    :context: Request context
    :param container_id: The id or uuid of a container.
    :values: The properties to be updated
    :returns: A container.
    :raises: ContainerNotFound
    """
    return _get_dbdriver_instance().update_container(
        context, container_id, values)

@profiler.trace("db")
def destroy_zun_service(host, binary):
    """Destroys a zun_service record.

    :param host: The host on which the service resides.
    :param binary: The binary file name of the service.
    :returns: A zun service record.
    """
    return _get_dbdriver_instance().destroy_zun_service(host, binary)


@profiler.trace("db")
def update_zun_service(host, binary, values):
    """Update properties of a zun_service.

    :param host: The host on which the service resides.
    :param binary: The binary file name of the service.
    :param values: The attributes to be updated.
    :returns: A zun service record.
    """
    return _get_dbdriver_instance().update_zun_service(host, binary, values)


@profiler.trace("db")
def get_zun_service(context, host, binary):
    """Return a zun_service record.

    :param context: The security context
    :param host: The host where the binary is located.
    :param binary: The name of the binary.
    :returns: A zun_service record.
    """
    return _get_dbdriver_instance().get_zun_service(host, binary)


@profiler.trace("db")
def create_zun_service(values):
    """Create a new zun_service record.

    :param values: A dict containing several items used to identify
                   and define the zun_service record.
    :returns: A zun_service record.
    """
    return _get_dbdriver_instance().create_zun_service(values)


@profiler.trace("db")
def list_zun_services(context, filters=None, limit=None,
                      marker=None, sort_key=None, sort_dir=None):
    """Get matching zun_service records.

    Return a list of the specified columns for all zun_services
    those match the specified filters.

    :param context: The security context
    :param disabled: Filters disbaled services. Defaults to None.
    :param limit: Maximum number of zun_services to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_zun_services(
        filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def list_zun_services_by_binary(context, binary):
    """List matching zun services.

    Return a list of the specified binary.
    :param context: The security context
    :param binary: The name of the binary.
    :returns: A list of tuples of the specified binary.
    """
    return _get_dbdriver_instance().list_zun_services_by_binary(binary)


@profiler.trace("db")
def pull_image(context, values):
    """Create a new image.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the image, and several dicts which are
                   passed
                   into the Drivers when managing this image. For
                   example:
                   ::
                    {
                     'uuid': uuidutils.generate_uuid(),
                     'repo': 'hello-world',
                     'tag': 'latest'
                    }
    :returns: An image.
    """
    return _get_dbdriver_instance().pull_image(context, values)


@profiler.trace("db")
def update_image(image_id, values):
    """Update properties of an image.

    :param container_id: The id or uuid of an image.
    :returns: An Image.
    :raises: ImageNotFound
    """
    return _get_dbdriver_instance().update_image(image_id, values)


@profiler.trace("db")
def list_images(context, filters=None,
                limit=None, marker=None,
                sort_key=None, sort_dir=None):
    """Get matching images.

    Return a list of the specified columns for all images that
    match the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of images to return.
    :param marker: the last item of the previous page; we
                    return the next
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_images(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def get_image_by_id(context, image_id):
    """Return an image.

    :param context: The security context
    :param image_id: The id of an image.
    :returns: An image.
    """
    return _get_dbdriver_instance().get_image_by_id(context, image_id)


@profiler.trace("db")
def get_image_by_uuid(context, image_uuid):
    """Return an image.

    :param context: The security context
    :param image_uuid: The uuid of an image.
    :returns: An image.
    """
    return _get_dbdriver_instance().get_image_by_uuid(context, image_uuid)


@profiler.trace("db")
def list_resource_users(context, filters=None, limit=None, marker=None,
                            sort_key=None, sort_dir=None):
    """Get matching resource users.

    Return a list of the specified columns for all resource users that
    match the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of resource users to return.
    :param marker: the last item of the previous page; we
                    return the next
    :param sort_key: Attribute by which results should be sorted.
                    (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_resource_users(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_resource_user(context, values):
    """Create a new resource user.

    :param context: The security context
    :param values: A dict containing several items used to identify and
                   track the resource user, and several dicts which are
                   passed into the Drivers when managing this resource
                   user.
    :returns: A resource user.
    """
    return _get_dbdriver_instance().create_resource_user(context, values)


@profiler.trace("db")
def get_resource_user(context, user_ident):
    """Return a resource user.

    :param context: The security context
    :param user_ident: The uuid or name of a resource user.
    :returns: A resource user.
    """
    return _get_dbdriver_instance().get_resource_user(
        context, user_ident)


@profiler.trace("db")
def destroy_resource_user(context, user_id):
    """Destroy a resource user and all associated interfaces.

    :param context: Request context
    :param user_id: The id or uuid of a resource user.
    """
    return _get_dbdriver_instance().destroy_resource_user(
        context, user_id)


@profiler.trace("db")
def update_resource_user(context, user_id, values):
    """Update properties of a resource user.

    :context: Request context
    :param user_id: The id or uuid of a resource user.
    :values: The properties to be updated
    :returns: A resource user.
    :raises: ResourceUserNotFound
    """
    return _get_dbdriver_instance().update_resource_user(
        context, user_id, values)


@profiler.trace("db")
def list_resource_classes(context, limit=None, marker=None, sort_key=None,
                          sort_dir=None):
    """Get matching resource classes.

    Return a list of the specified columns for all resource classes.
    :param context: The security context
    :param limit: Maximum number of resource classes to return.
    :param marker: the last item of the previous page; we
                    return the next
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_resource_classes(
        context, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_resource_class(context, values):
    """Create a new resource class.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the resource class, and several dicts which are
                   passed into the Drivers when managing this resource class.
    :returns: A resource class.
    """
    return _get_dbdriver_instance().create_resource_class(context, values)


@profiler.trace("db")
def get_resource_class(context, resource_ident):
    """Return a resource class.

    :param context: The security context
    :param resource_ident: The uuid or name of a resource class.
    :returns: A resource class.
    """
    return _get_dbdriver_instance().get_resource_class(
        context, resource_ident)


@profiler.trace("db")
def destroy_resource_class(context, resource_uuid):
    """Destroy a resource class and all associated interfaces.

    :param context: Request context
    :param resource_uuid: The uuid of a resource class.
    """
    return _get_dbdriver_instance().destroy_resource_class(
        context, resource_uuid)


@profiler.trace("db")
def update_resource_class(context, resource_uuid, values):
    """Update properties of a resource class.

    :context: Request context
    :param resource_uuid: The uuid of a resource class.
    :values: The properties to be updated
    :returns: A resource class.
    :raises: ResourceClassNotFound
    """
    return _get_dbdriver_instance().update_resource_class(
        context, resource_uuid, values)


@profiler.trace("db")
def list_inventories(context, filters=None, limit=None, marker=None,
                     sort_key=None, sort_dir=None):
    """List matching inventories.

    Return a list of the specified columns for all inventories that match
    the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of inventories to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_inventories(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_inventory(context, user_id, values):
    """Create a new inventory.

    :param context: The security context
    :param user_id: The id of a resource user.
    :param values: A dict containing several items used to identify
                   and track the inventory, and several dicts which are
                   passed into the Drivers when managing this inventory.
    :returns: An inventory.
    """
    return _get_dbdriver_instance().create_inventory(
        context, user_id, values)


@profiler.trace("db")
def get_inventory(context, inventory_ident):
    """Return a inventory.

    :param context: The security context
    :param inventory_ident: The id or name of an inventory.
    :returns: An inventory.
    """
    return _get_dbdriver_instance().get_inventory(
        context, inventory_ident)


@profiler.trace("db")
def destroy_inventory(context, inventory_id):
    """Destroy an inventory and all associated interfaces.

    :param context: Request context
    :param inventory_id: The id of a inventory.
    """
    return _get_dbdriver_instance().destroy_inventory(context, inventory_id)


@profiler.trace("db")
def update_inventory(context, inventory_id, values):
    """Update properties of an inventory.

    :context: Request context
    :param inventory_id: The id of an inventory.
    :values: The properties to be updated
    :returns: An inventory.
    :raises: InventoryNotFound
    """
    return _get_dbdriver_instance().update_inventory(
        context, inventory_id, values)


@profiler.trace("db")
def list_allocations(context, filters=None, limit=None, marker=None,
                     sort_key=None, sort_dir=None):
    """List matching allocations.

    Return a list of the specified columns for all allocations that match
    the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of allocations to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_allocations(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_allocation(context, values):
    """Create a new allocation.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the allocation, and several dicts which are
                   passed into the Drivers when managing this allocation.
    :returns: An allocation.
    """
    return _get_dbdriver_instance().create_allocation(context, values)


@profiler.trace("db")
def get_allocation(context, allocation_id):
    """Return an allocation.

    :param context: The security context
    :param allocation_id: The id of an allocation.
    :returns: An allocation.
    """
    return _get_dbdriver_instance().get_allocation(context, allocation_id)


@profiler.trace("db")
def destroy_allocation(context, allocation_id):
    """Destroy an allocation and all associated interfaces.

    :param context: Request context
    :param allocation_id: The id of an allocation.
    """
    return _get_dbdriver_instance().destroy_allocation(context, allocation_id)


@profiler.trace("db")
def update_allocation(context, allocation_id, values):
    """Update properties of an allocation.

    :context: Request context
    :param allocation_id: The id of an allocation.
    :values: The properties to be updated
    :returns: An allocation.
    :raises: AllocationNotFound
    """
    return _get_dbdriver_instance().update_allocation(
        context, allocation_id, values)


@profiler.trace("db")
def list_compute_nodes(context, filters=None, limit=None, marker=None,
                       sort_key=None, sort_dir=None):
    """List matching compute nodes.

    Return a list of the specified columns for all compute nodes that match
    the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of compute nodes to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_compute_nodes(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_compute_node(context, values):
    """Create a new compute node.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the compute node, and several dicts which are
                   passed into the Drivers when managing this compute node.
    :returns: A compute node.
    """
    return _get_dbdriver_instance().create_compute_node(context, values)


@profiler.trace("db")
def get_compute_node(context, node_uuid):
    """Return a compute node.

    :param context: The security context
    :param node_uuid: The uuid of a compute node.
    :returns: A compute node.
    """
    return _get_dbdriver_instance().get_compute_node(context, node_uuid)


@profiler.trace("db")
def get_compute_node_by_hostname(context, hostname):
    """Return a compute node.

    :param context: The security context
    :param hostname: The hostname of a compute node.
    :returns: A compute node.
    """
    return _get_dbdriver_instance().get_compute_node_by_hostname(
        context, hostname)


@profiler.trace("db")
def destroy_compute_node(context, node_uuid):
    """Destroy a compute node and all associated interfaces.

    :param context: Request context
    :param node_uuid: The uuid of a compute node.
    """
    return _get_dbdriver_instance().destroy_compute_node(context, node_uuid)


@profiler.trace("db")
def update_compute_node(context, node_uuid, values):
    """Update properties of a compute node.

    :context: Request context
    :param node_uuid: The uuid of a compute node.
    :values: The properties to be updated
    :returns: A compute node.
    :raises: ComputeNodeNotFound
    """
    return _get_dbdriver_instance().update_compute_node(
        context, node_uuid, values)


@profiler.trace("db")
def list_capsules(context, filters=None, limit=None, marker=None,
                  sort_key=None, sort_dir=None):
    """List matching capsules.

    Return a list of the specified columns for all capsules that match
    the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of capsules to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_capsules(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_capsule(context, values):
    """Create a new capsule.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the container, and several dicts which are
                   passed into the Drivers when managing this container.
                   For example:
                   ::
                    {
                     'uuid': uuidutils.generate_uuid(),
                     'restart_policy': 'always',
                     'project_id': '***'
                    }
    :returns: A capsule.
    """
    return _get_dbdriver_instance().create_capsule(context, values)


@profiler.trace("db")
def get_capsule_by_uuid(context, capsule_uuid):
    """Return a container.

    :param context: The security context
    :param capsule_uuid: The uuid of a capsule.
    :returns: A capsule.
    """
    return _get_dbdriver_instance().get_capsule_by_uuid(
        context, capsule_uuid)


@profiler.trace("db")
def destroy_capsule(context, capsule_id):
    """Destroy a container and all associated interfaces.

    :param context: Request context
    :param capsule_id: The id or uuid of a capsule.
    """
    return _get_dbdriver_instance().destroy_capsule(context, capsule_id)


@profiler.trace("db")
def update_capsule(context, capsule_id, values):
    """Update properties of a container.

    :context: Request context
    :param container_id: The id or uuid of a capsule.
    :values: The properties to be updated
    :returns: A capsule.
    :raises: CapsuleNotFound
    """
    return _get_dbdriver_instance().update_capsule(
        context, capsule_id, values)
