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
def list_storagerates(context, filters=None, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
    """List matching storagerates.

    Return a list of the specified columns for all storagerates that match
    the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of storagerates to return.
    :param marker: the last item of the previous page; we return the next
                   result set.
    :param sort_key: Attribute by which results should be sorted.
    :param sort_dir: Direction in which results should be sorted.
                     (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_storagerates(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_storagerate(context, values):
    """Create a new storagerate.

    :param context: The security context
    :param values: A dict containing several items used to identify
                   and track the storagerate, and several dicts which are
                   passed
                   into the Drivers when managing this storagerate. For
                   example:
                   ::
                    {
                     'uuid': uuidutils.generate_uuid(),
                     'name': 'example',
                     'type': 'virt'
                    }
    :returns: A storagerate.
    """
    return _get_dbdriver_instance().create_storagerate(context, values)


@profiler.trace("db")
def get_storagerate_by_uuid(context, storagerate_uuid):
    """Return a storagerate.

    :param context: The security context
    :param storagerate_uuid: The uuid of a storagerate.
    :returns: A storagerate.
    """
    return _get_dbdriver_instance().get_storagerate_by_uuid(
        context, storagerate_uuid)


@profiler.trace("db")
def get_storagerate_by_name(context, storagerate_name):
    """Return a storagerate.

    :param context: The security context
    :param storagerate_name: The name of a storagerate.
    :returns: A storagerate.
    """
    return _get_dbdriver_instance().get_storagerate_by_name(
        context, storagerate_name)


@profiler.trace("db")
def destroy_storagerate(context, storagerate_id):
    """Destroy a storagerate and all associated interfaces.

    :param context: Request context
    :param storagerate_id: The id or uuid of a storagerate.
    """
    return _get_dbdriver_instance().destroy_storagerate(context, storagerate_id)


@profiler.trace("db")
def update_storagerate(context, storagerate_id, values):
    """Update properties of a storagerate.

    :context: Request context
    :param storagerate_id: The id or uuid of a storagerate.
    :values: The properties to be updated
    :returns: A storagerate.
    :raises: ContainerNotFound
    """
    process_date("start_time", values)
    process_date("end_time", values)
    return _get_dbdriver_instance().update_storagerate(
        context, storagerate_id, values)

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
def list_resource_storagerates(context, filters=None, limit=None, marker=None,
                            sort_key=None, sort_dir=None):
    """Get matching resource storagerates.

    Return a list of the specified columns for all resource storagerates that
    match the specified filters.
    :param context: The security context
    :param filters: Filters to apply. Defaults to None.
    :param limit: Maximum number of resource storagerates to return.
    :param marker: the last item of the previous page; we
                    return the next
    :param sort_key: Attribute by which results should be sorted.
                    (asc, desc)
    :returns: A list of tuples of the specified columns.
    """
    return _get_dbdriver_instance().list_resource_storagerates(
        context, filters, limit, marker, sort_key, sort_dir)


@profiler.trace("db")
def create_resource_storagerate(context, values):
    """Create a new resource storagerate.

    :param context: The security context
    :param values: A dict containing several items used to identify and
                   track the resource storagerate, and several dicts which are
                   passed into the Drivers when managing this resource
                   storagerate.
    :returns: A resource storagerate.
    """
    return _get_dbdriver_instance().create_resource_storagerate(context, values)


@profiler.trace("db")
def get_resource_storagerate(context, storagerate_ident):
    """Return a resource storagerate.

    :param context: The security context
    :param storagerate_ident: The uuid or name of a resource storagerate.
    :returns: A resource storagerate.
    """
    return _get_dbdriver_instance().get_resource_storagerate(
        context, storagerate_ident)


@profiler.trace("db")
def destroy_resource_storagerate(context, storagerate_id):
    """Destroy a resource storagerate and all associated interfaces.

    :param context: Request context
    :param storagerate_id: The id or uuid of a resource storagerate.
    """
    return _get_dbdriver_instance().destroy_resource_storagerate(
        context, storagerate_id)


@profiler.trace("db")
def update_resource_storagerate(context, storagerate_id, values):
    """Update properties of a resource storagerate.

    :context: Request context
    :param storagerate_id: The id or uuid of a resource storagerate.
    :values: The properties to be updated
    :returns: A resource storagerate.
    :raises: ResourceStoragerateNotFound
    """
    return _get_dbdriver_instance().update_resource_storagerate(
        context, storagerate_id, values)


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
def create_inventory(context, storagerate_id, values):
    """Create a new inventory.

    :param context: The security context
    :param storagerate_id: The id of a resource storagerate.
    :param values: A dict containing several items used to identify
                   and track the inventory, and several dicts which are
                   passed into the Drivers when managing this inventory.
    :returns: An inventory.
    """
    return _get_dbdriver_instance().create_inventory(
        context, storagerate_id, values)


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
