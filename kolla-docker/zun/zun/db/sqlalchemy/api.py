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

"""SQLAlchemy storage backend."""
import logging
LOG = logging.getLogger(__name__)

from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from oslo_db.sqlalchemy import utils as db_utils
from oslo_utils import importutils
from oslo_utils import strutils
from oslo_utils import timeutils
from oslo_utils import uuidutils
import sqlalchemy as sa
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql import func

from zun.common import consts
from zun.common import exception
from zun.common.i18n import _
import zun.conf
from zun.db.sqlalchemy import models

profiler_sqlalchemy = importutils.try_import('osprofiler.sqlalchemy')

CONF = zun.conf.CONF

_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.enginefacade.get_legacy_facade()
        if profiler_sqlalchemy:
            if CONF.profiler.enabled and CONF.profiler.trace_sqlalchemy:
                profiler_sqlalchemy.add_tracing(sa, _FACADE.get_engine(), "db")
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    """The backend is this module itself."""
    return Connection()


def model_query(model, *args, **kwargs):
    """Query helper for simpler session usage.

    :param session: if present, the session to use
    """

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


def add_identity_filter(query, value):
    """Adds an identity filter to a query.

    Filters results by ID, if supplied value is a valid integer.
    Otherwise attempts to filter results by UUID.

    :param query: Initial query to add filter to.
    :param value: Value for filtering results by.
    :return: Modified query.
    """
    if strutils.is_int_like(value):
        return query.filter_by(id=value)
    elif uuidutils.is_uuid_like(value):
        return query.filter_by(uuid=value)
    else:
        raise exception.InvalidIdentity(identity=value)


def _paginate_query(model, limit=None, marker=None, sort_key=None,
                    sort_dir=None, query=None, default_sort_key='id'):
    if not query:
        query = model_query(model)
    sort_keys = [default_sort_key]
    if sort_key and sort_key not in sort_keys:
        sort_keys.insert(0, sort_key)
    try:
        query = db_utils.paginate_query(query, model, limit, sort_keys,
                                        marker=marker, sort_dir=sort_dir)
    except db_exc.InvalidSortKey:
        raise exception.InvalidParameterValue(
            _('The sort_key value "%(key)s" is an invalid field for sorting')
            % {'key': sort_key})
    LOG.info("query.all() query.all() query.all() query.all() query.all() query.all() query.all() query.all() query.all() query.all() query.all()")
    LOG.info(query.all())
    return query.all()


class Connection(object):
    """SqlAlchemy connection."""

    def __init__(self):
        pass

    def _add_project_filters(self, context, query):
        if context.is_admin and context.all_projects:
            return query

        if context.project_id:
            query = query.filter_by(project_id=context.project_id)
        else:
            query = query.filter_by(user_id=context.user_id)

        return query

    def _add_containers_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['name', 'image', 'project_id', 'user_id',
                        'memory', 'host', 'task_state', 'status',
                        'auto_remove']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_containers(self, context, filters=None, limit=None,
                        marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Container)
        query = self._add_project_filters(context, query)
        query = self._add_containers_filters(query, filters)
        return _paginate_query(models.Container, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_container_name(self, context, name):
        if not CONF.compute.unique_container_name_scope:
            return
        lowername = name.lower()
        base_query = model_query(models.Container).\
            filter(func.lower(models.Container.name) == lowername)
        if CONF.compute.unique_container_name_scope == 'project':
            container_with_same_name = base_query.\
                filter_by(project_id=context.project_id).count()
        elif CONF.compute.unique_container_name_scope == 'global':
            container_with_same_name = base_query.count()
        else:
            return

        if container_with_same_name > 0:
            raise exception.ContainerAlreadyExists(field='name',
                                                   value=lowername)

    def create_container(self, context, values):
        # ensure defaults are present for new containers
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_container_name(context, values['name'])

        container = models.Container()
        container.update(values)
        try:
            container.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ContainerAlreadyExists(field='UUID',
                                                   value=values['uuid'])
        return container

    def get_container_by_uuid(self, context, container_uuid):
        query = model_query(models.Container)
        query = self._add_project_filters(context, query)
        query = query.filter_by(uuid=container_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ContainerNotFound(container=container_uuid)

    def get_container_by_name(self, context, container_name):
        query = model_query(models.Container)
        query = self._add_project_filters(context, query)
        query = query.filter_by(name=container_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ContainerNotFound(container=container_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple containers exist with same '
                                     'name. Please use the container uuid '
                                     'instead.')

    def destroy_container(self, context, container_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Container, session=session)
            query = add_identity_filter(query, container_id)
            count = query.delete()
            if count != 1:
                raise exception.ContainerNotFound(container_id)

    def update_container(self, context, container_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Container.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_container_name(context, values['name'])

        return self._do_update_container(container_id, values)

    def _do_update_container(self, container_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Container, session=session)
            query = add_identity_filter(query, container_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ContainerNotFound(container=container_id)

            ref.update(values)
        return ref

    def _add_volume_mappings_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['project_id', 'user_id', 'volume_id', 'container_path',
                        'container_uuid', 'volume_provider']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_volume_mappings(self, context, filters=None, limit=None,
                             marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.VolumeMapping)
        query = self._add_project_filters(context, query)
        query = self._add_volume_mappings_filters(query, filters)
        return _paginate_query(models.VolumeMapping, limit, marker,
                               sort_key, sort_dir, query)

    def create_volume_mapping(self, context, values):
        # ensure defaults are present for new volume_mappings
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        volume_mapping = models.VolumeMapping()
        volume_mapping.update(values)
        try:
            volume_mapping.save()
        except db_exc.DBDuplicateEntry:
            raise exception.VolumeMappingAlreadyExists(field='UUID',
                                                       value=values['uuid'])
        return volume_mapping

    def get_volume_mapping_by_uuid(self, context, volume_mapping_uuid):
        query = model_query(models.VolumeMapping)
        query = self._add_project_filters(context, query)
        query = query.filter_by(uuid=volume_mapping_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.VolumeMappingNotFound(volume_mapping_uuid)

    def destroy_volume_mapping(self, context, volume_mapping_uuid):
        session = get_session()
        with session.begin():
            query = model_query(models.VolumeMapping, session=session)
            query = add_identity_filter(query, volume_mapping_uuid)
            count = query.delete()
            if count != 1:
                raise exception.VolumeMappingNotFound(
                    volume_mapping_uuid)

    def update_volume_mapping(self, context, volume_mapping_uuid, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing VolumeMapping.")
            raise exception.InvalidParameterValue(err=msg)

        return self._do_update_volume_mapping(volume_mapping_uuid, values)

    def _do_update_volume_mapping(self, volume_mapping_uuid, values):
        session = get_session()
        with session.begin():
            query = model_query(models.VolumeMapping, session=session)
            query = add_identity_filter(query, volume_mapping_uuid)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.VolumeMappingNotFound(volume_mapping_uuid)

            ref.update(values)
        return ref

    def destroy_zun_service(self, host, binary):
        session = get_session()
        with session.begin():
            query = model_query(models.ZunService, session=session)
            query = query.filter_by(host=host, binary=binary)
            count = query.delete()
            if count != 1:
                raise exception.ZunServiceNotFound(host=host, binary=binary)

    def update_zun_service(self, host, binary, values):
        session = get_session()
        with session.begin():
            query = model_query(models.ZunService, session=session)
            query = query.filter_by(host=host, binary=binary)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ZunServiceNotFound(host=host, binary=binary)

            if 'report_count' in values:
                if values['report_count'] > ref.report_count:
                    ref.last_seen_up = timeutils.utcnow()

            ref.update(values)
        return ref

    def get_zun_service(self, host, binary):
        query = model_query(models.ZunService)
        query = query.filter_by(host=host, binary=binary)
        try:
            return query.one()
        except NoResultFound:
            return None

    def create_zun_service(self, values):
        zun_service = models.ZunService()
        zun_service.update(values)
        try:
            zun_service.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ZunServiceAlreadyExists(
                host=zun_service.host, binary=zun_service.binary)
        return zun_service

    def _add_zun_service_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['disabled', 'host', 'binary', 'project_id', 'user_id']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_zun_services(self, filters=None, limit=None, marker=None,
                          sort_key=None, sort_dir=None):
        query = model_query(models.ZunService)
        if filters:
            query = self._add_zun_service_filters(query, filters)

        return _paginate_query(models.ZunService, limit, marker,
                               sort_key, sort_dir, query)

    def list_zun_services_by_binary(self, binary):
        query = model_query(models.ZunService)
        query = query.filter_by(binary=binary)
        return _paginate_query(models.ZunService, query=query)

    def pull_image(self, context, values):
        # ensure defaults are present for new images
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()
        image = models.Image()
        image.update(values)
        try:
            image.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ImageAlreadyExists(tag=values['tag'],
                                               repo=values['repo'])
        return image

    def update_image(self, image_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Image.")
            raise exception.InvalidParameterValue(err=msg)
        return self._do_update_image(image_id, values)

    def _do_update_image(self, image_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Image, session=session)
            query = add_identity_filter(query, image_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ImageNotFound(image=image_id)

            ref.update(values)
        return ref

    def _add_image_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['repo', 'project_id', 'user_id', 'size']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_images(self, context, filters=None, limit=None, marker=None,
                    sort_key=None, sort_dir=None):
        query = model_query(models.Image)
        query = self._add_project_filters(context, query)
        query = self._add_image_filters(query, filters)
        return _paginate_query(models.Image, limit, marker, sort_key,
                               sort_dir, query)

    def get_image_by_id(self, context, image_id):
        query = model_query(models.Image)
        query = self._add_project_filters(context, query)
        query = query.filter_by(id=image_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ImageNotFound(image=image_id)

    def get_image_by_uuid(self, context, image_uuid):
        query = model_query(models.Image)
        query = self._add_project_filters(context, query)
        query = query.filter_by(uuid=image_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ImageNotFound(image=image_uuid)

    def _add_resource_providers_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['name', 'root_provider', 'parent_provider', 'can_host']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_resource_providers(self, context, filters=None, limit=None,
                                marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.ResourceProvider)
        query = self._add_resource_providers_filters(query, filters)
        return _paginate_query(models.ResourceProvider, limit, marker,
                               sort_key, sort_dir, query)

    def create_resource_provider(self, context, values):
        # ensure defaults are present for new resource providers
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        resource_provider = models.ResourceProvider()
        resource_provider.update(values)
        try:
            resource_provider.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ResourceProviderAlreadyExists(
                field='UUID', value=values['uuid'])
        return resource_provider

    def get_resource_provider(self, context, provider_ident):
        if uuidutils.is_uuid_like(provider_ident):
            return self._get_resource_provider_by_uuid(context, provider_ident)
        else:
            return self._get_resource_provider_by_name(context, provider_ident)

    def _get_resource_provider_by_uuid(self, context, provider_uuid):
        query = model_query(models.ResourceProvider)
        query = query.filter_by(uuid=provider_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ResourceProviderNotFound(
                resource_provider=provider_uuid)

    def _get_resource_provider_by_name(self, context, provider_name):
        query = model_query(models.ResourceProvider)
        query = query.filter_by(name=provider_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ResourceProviderNotFound(
                resource_provider=provider_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple resource providers exist with '
                                     'same name. Please use the uuid instead.')

    def destroy_resource_provider(self, context, provider_id):
        session = get_session()
        with session.begin():
            query = model_query(models.ResourceProvider, session=session)
            query = add_identity_filter(query, provider_id)
            count = query.delete()
            if count != 1:
                raise exception.ResourceProviderNotFound(
                    resource_provider=provider_id)

    def update_resource_provider(self, context, provider_id, values):
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing ResourceProvider.")
            raise exception.InvalidParameterValue(err=msg)

        return self._do_update_resource_provider(provider_id, values)

    def _do_update_resource_provider(self, provider_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.ResourceProvider, session=session)
            query = add_identity_filter(query, provider_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ResourceProviderNotFound(
                    resource_provider=provider_id)

            ref.update(values)
        return ref

    def list_resource_classes(self, context, limit=None, marker=None,
                              sort_key=None, sort_dir=None):
        query = model_query(models.ResourceClass)
        return _paginate_query(models.ResourceClass, limit, marker,
                               sort_key, sort_dir, query)

    def create_resource_class(self, context, values):
        resource = models.ResourceClass()
        resource.update(values)
        try:
            resource.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ResourceClassAlreadyExists(
                field='uuid', value=values['uuid'])
        return resource

    def get_resource_class(self, context, resource_ident):
        if uuidutils.is_uuid_like(resource_ident):
            return self._get_resource_class_by_uuid(context, resource_ident)
        else:
            return self._get_resource_class_by_name(context, resource_ident)

    def _get_resource_class_by_uuid(self, context, resource_uuid):
        query = model_query(models.ResourceClass)
        query = query.filter_by(uuid=resource_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ResourceClassNotFound(
                resource_class=resource_uuid)

    def _get_resource_class_by_name(self, context, resource_name):
        query = model_query(models.ResourceClass)
        query = query.filter_by(name=resource_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ResourceClassNotFound(resource_class=resource_name)

    def destroy_resource_class(self, context, resource_id):
        session = get_session()
        with session.begin():
            query = model_query(models.ResourceClass, session=session)
            count = query.delete()
            if count != 1:
                raise exception.ResourceClassNotFound(
                    resource_class=str(resource_id))

    def update_resource_class(self, context, resource_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.ResourceClass, session=session)
            query = query.filter_by(id=resource_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ResourceClassNotFound(
                    resource_class=resource_id)

            ref.update(values)
        return ref

    def _add_inventories_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['resource_provider_id', 'resource_class_id', 'total',
                        'reserved', 'min_unit', 'max_unit', 'step_size',
                        'allocation_ratio', 'is_nested']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_inventories(self, context, filters=None, limit=None,
                         marker=None, sort_key=None, sort_dir=None):
        session = get_session()
        query = model_query(models.Inventory, session=session)
        query = self._add_inventories_filters(query, filters)
        query = query.join(models.Inventory.resource_provider)
        query = query.options(contains_eager('resource_provider'))
        return _paginate_query(models.Inventory, limit, marker,
                               sort_key, sort_dir, query)

    def create_inventory(self, context, provider_id, values):
        values['resource_provider_id'] = provider_id
        inventory = models.Inventory()
        inventory.update(values)
        try:
            inventory.save()
        except db_exc.DBDuplicateEntry as e:
            fields = {c: values[c] for c in e.columns}
            raise exception.UniqueConstraintViolated(fields=fields)
        return inventory

    def get_inventory(self, context, inventory_id):
        session = get_session()
        query = model_query(models.Inventory, session=session)
        query = query.join(models.Inventory.resource_provider)
        query = query.options(contains_eager('resource_provider'))
        query = query.filter_by(id=inventory_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InventoryNotFound(inventory=inventory_id)

    def destroy_inventory(self, context, inventory_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Inventory, session=session)
            query = query.filter_by(id=inventory_id)
            count = query.delete()
            if count != 1:
                raise exception.InventoryNotFound(inventory=inventory_id)

    def update_inventory(self, context, inventory_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Inventory, session=session)
            query = query.filter_by(id=inventory_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.InventoryNotFound(inventory=inventory_id)

            ref.update(values)
        return ref

    def _add_allocations_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['resource_provider_id', 'resource_class_id',
                        'consumer_id', 'used', 'is_nested']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_allocations(self, context, filters=None, limit=None,
                         marker=None, sort_key=None, sort_dir=None):
        session = get_session()
        query = model_query(models.Allocation, session=session)
        query = self._add_allocations_filters(query, filters)
        query = query.join(models.Allocation.resource_provider)
        query = query.options(contains_eager('resource_provider'))
        return _paginate_query(models.Allocation, limit, marker,
                               sort_key, sort_dir, query)

    def create_allocation(self, context, values):
        allocation = models.Allocation()
        allocation.update(values)
        try:
            allocation.save()
        except db_exc.DBDuplicateEntry as e:
            fields = {c: values[c] for c in e.columns}
            raise exception.UniqueConstraintViolated(fields=fields)
        return allocation

    def get_allocation(self, context, allocation_id):
        session = get_session()
        query = model_query(models.Allocation, session=session)
        query = query.join(models.Allocation.resource_provider)
        query = query.options(contains_eager('resource_provider'))
        query = query.filter_by(id=allocation_id)
        try:
            return query.one()
        except NoResultFound:
            raise exception.AllocationNotFound(allocation=allocation_id)

    def destroy_allocation(self, context, allocation_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Allocation, session=session)
            query = query.filter_by(id=allocation_id)
            count = query.delete()
            if count != 1:
                raise exception.AllocationNotFound(allocation=allocation_id)

    def update_allocation(self, context, allocation_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Allocation, session=session)
            query = query.filter_by(id=allocation_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.AllocationNotFound(allocation=allocation_id)

            ref.update(values)
        return ref

    def _add_compute_nodes_filters(self, query, filters):
        if not filters:
            return query

        filter_names = ['hostname']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_compute_nodes(self, context, filters=None, limit=None,
                           marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.ComputeNode)
        query = self._add_compute_nodes_filters(query, filters)
        return _paginate_query(models.ComputeNode, limit, marker,
                               sort_key, sort_dir, query,
                               default_sort_key='uuid')

    def create_compute_node(self, context, values):
        # ensure defaults are present for new compute nodes
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        compute_node = models.ComputeNode()
        compute_node.update(values)
        try:
            compute_node.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ComputeNodeAlreadyExists(
                field='UUID', value=values['uuid'])
        return compute_node

    def get_compute_node(self, context, node_uuid):
        query = model_query(models.ComputeNode)
        query = query.filter_by(uuid=node_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputeNodeNotFound(
                compute_node=node_uuid)

    def get_compute_node_by_hostname(self, context, hostname):
        query = model_query(models.ComputeNode)
        query = query.filter_by(hostname=hostname)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputeNodeNotFound(
                compute_node=hostname)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple compute nodes exist with same '
                                     'hostname. Please use the uuid instead.')

    def destroy_compute_node(self, context, node_uuid):
        session = get_session()
        with session.begin():
            query = model_query(models.ComputeNode, session=session)
            query = query.filter_by(uuid=node_uuid)
            count = query.delete()
            if count != 1:
                raise exception.ComputeNodeNotFound(
                    compute_node=node_uuid)

    def update_compute_node(self, context, node_uuid, values):
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing ComputeNode.")
            raise exception.InvalidParameterValue(err=msg)

        return self._do_update_compute_node(node_uuid, values)

    def _do_update_compute_node(self, node_uuid, values):
        session = get_session()
        with session.begin():
            query = model_query(models.ComputeNode, session=session)
            query = query.filter_by(uuid=node_uuid)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ComputeNodeNotFound(
                    compute_node=node_uuid)

            ref.update(values)
        return ref

    def list_capsules(self, context, filters=None, limit=None,
                      marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Capsule)
        query = self._add_project_filters(context, query)
        query = self._add_capsules_filters(query, filters)
        return _paginate_query(models.Capsule, limit, marker,
                               sort_key, sort_dir, query)

    def create_capsule(self, context, values):
        # ensure defaults are present for new capsules
        # here use the infra container uuid as the capsule uuid
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()
        capsule = models.Capsule()
        capsule.update(values)
        try:
            capsule.save()
        except db_exc.DBDuplicateEntry:
            raise exception.CapsuleAlreadyExists(field='UUID',
                                                 value=values['uuid'])
        return capsule

    def get_capsule_by_uuid(self, context, capsule_uuid):
        query = model_query(models.Capsule)
        query = self._add_project_filters(context, query)
        query = query.filter_by(uuid=capsule_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.CapsuleNotFound(capsule=capsule_uuid)

    def get_capsule_by_meta_name(self, context, capsule_name):
        query = model_query(models.Capsule)
        query = self._add_project_filters(context, query)
        query = query.filter_by(meta_name=capsule_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.CapsuleNotFound(capsule=capsule_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple capsules exist with same '
                                     'name. Please use the capsule uuid '
                                     'instead.')

    def destroy_capsule(self, context, capsule_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Capsule, session=session)
            query = add_identity_filter(query, capsule_id)
            count = query.delete()
            if count != 1:
                raise exception.CapsuleNotFound(capsule_id)

    def update_capsule(self, context, capsule_id, values):
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Capsule.")
            raise exception.InvalidParameterValue(err=msg)

        return self._do_update_capsule_id(capsule_id, values)

    def _do_update_capsule_id(self, capsule_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Capsule, session=session)
            query = add_identity_filter(query, capsule_id)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.CapsuleNotFound(capsule=capsule_id)

            ref.update(values)
        return ref

    def _add_capsules_filters(self, query, filters):
        if not filters:
            return query

        # filter_names = ['uuid', 'project_id', 'user_id', 'containers']
        filter_names = ['uuid', 'project_id', 'user_id']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def get_pci_device_by_addr(self, node_id, dev_addr):
        pci_dev_ref = model_query(models.PciDevice).\
            filter_by(compute_node_uuid=node_id).\
            filter_by(address=dev_addr).\
            first()
        if not pci_dev_ref:
            raise exception.PciDeviceNotFound(node_id=node_id,
                                              address=dev_addr)
        return pci_dev_ref

    def get_pci_device_by_id(self, id):
        pci_dev_ref = model_query(models.PciDevice).\
            filter_by(id=id).\
            first()
        if not pci_dev_ref:
            raise exception.PciDeviceNotFoundById(id=id)
        return pci_dev_ref

    def get_all_pci_device_by_node(self, node_id):
        return model_query(models.PciDevice).\
            filter_by(compute_node_uuid=node_id).\
            all()

    def get_all_pci_device_by_parent_addr(self, node_id, parent_addr):
        return model_query(models.PciDevice).\
            filter_by(compute_node_uuid=node_id).\
            filter_by(parent_addr=parent_addr).\
            all()

    def get_all_pci_device_by_container_uuid(self, container_uuid):
        return model_query(models.PciDevice).\
            filter_by(status=consts.ALLOCATED).\
            filter_by(container_uuid=container_uuid).\
            all()

    def destroy_pci_device(self, node_id, address):
        session = get_session()
        with session.begin():
            query = model_query(models.PciDevice).\
                filter_by(compute_node_uuid=node_id).\
                filter_by(address=address)
            count = query.delete()
            if count != 1:
                raise exception.PciDeviceNotFound(node_id=node_id,
                                                  address=address)

    def update_pci_device(self, node_id, address, values):
        query = model_query(models.PciDevice).\
            filter_by(compute_node_uuid=node_id).\
            filter_by(address=address)
        if query.update(values) == 0:
            device = models.PciDevice()
            device.update(values)
            device.save()
        return query.one()

    def action_start(self, context, values):
        action = models.ContainerAction()
        action.update(values)
        action.save()
        return action

    def actions_get(self, context, container_uuid):
        """Get all container actions for the provided uuid."""
        query = model_query(models.ContainerAction).\
            filter_by(container_uuid=container_uuid)
        actions = _paginate_query(models.ContainerAction, sort_dir='desc',
                                  sort_key='created_at', query=query)

        return actions

    def action_get_by_request_id(self, context, container_uuid, request_id):
        """Get the action by request_id and given container."""
        action = self._action_get_by_request_id(context, container_uuid,
                                                request_id)
        return action

    def _action_get_by_request_id(self, context, container_uuid, request_id):
        result = model_query(models.ContainerAction).\
            filter_by(container_uuid=container_uuid).\
            filter_by(request_id=request_id).\
            first()
        return result

    def _action_get_last_created_by_container_uuid(self, context,
                                                   container_uuid):
        result = model_query(models.ContainerAction).\
            filter_by(container_uuid=container_uuid).\
            order_by(desc("created_at"), desc("id")).\
            first()
        return result

    def action_event_start(self, context, values):
        """Start an event on a container action."""
        action = self._action_get_by_request_id(context,
                                                values['container_uuid'],
                                                values['request_id'])

        # When zun-compute restarts, the request_id was different with
        # request_id recorded in ContainerAction, so we can't get the original
        # recode according to request_id. Try to get the last created action
        # so that init_container can continue to finish the recovery action.
        if not action and not context.project_id:
            action = self._action_get_last_created_by_container_uuid(
                context, values['container_uuid'])

        if not action:
            raise exception.ContainerActionNotFound(
                request_id=values['request_id'],
                container_uuid=values['container_uuid'])

        values['action_id'] = action['id']

        event = models.ContainerActionEvent()
        event.update(values)
        event.save()

        return event

    def action_event_finish(self, context, values):
        """Finish an event on a container action."""
        action = self._action_get_by_request_id(context,
                                                values['container_uuid'],
                                                values['request_id'])

        # When zun-compute restarts, the request_id was different with
        # request_id recorded in ContainerAction, so we can't get the original
        # recode according to request_id. Try to get the last created action
        # so that init_container can continue to finish the recovery action.
        if not action and not context.project_id:
            action = self._action_get_last_created_by_container_uuid(
                context, values['container_uuid'])

        if not action:
            raise exception.ContainerActionNotFound(
                request_id=values['request_id'],
                container_uuid=values['container_uuid'])
        event = model_query(models.ContainerActionEvent).\
            filter_by(action_id=action['id']).\
            filter_by(event=values['event']).\
            first()

        if not event:
            raise exception.ContainerActionEventNotFound(
                action_id=action['id'], event=values['event'])

        event.update(values)
        event.save()

        if values['result'].lower() == 'error':
            action.update({'message': 'Error'})
            action.save()

        return event

    def action_events_get(self, context, action_id):
        query = model_query(models.ContainerActionEvent).\
            filter_by(action_id=action_id)
        events = _paginate_query(models.ContainerActionEvent, sort_dir='desc',
                                 sort_key='created_at', query=query)
        return events
    # user section
    def _add_users_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_users(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.User)
        # query = self._add_tenant_filters(context, query)
        query = self._add_users_filters(query, filters)
        LOG.info('list_users list_users list_users list_users list_users list_users list_users list_users list_users list_users list_users list_users')
        LOG.info(filters)
        LOG.info(limit)
        LOG.info(marker)
        LOG.info(sort_key)
        LOG.info(sort_dir)

        LOG.debug('sqlalchemy api.py list_users xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of users is %s', (sort_key))
        return _paginate_query(models.User, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_user_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.User). \
            filter(func.lower(models.User.name) == lowername)
        user_with_same_name = base_query.count()
        if user_with_same_name > 0:
            raise exception.UserAlreadyExists(field='name',
                                                  value=lowername)

    def create_user(self, context, values):
        # ensure defaults are present for new users
        LOG.debug('sqlalchemy api.py create_user xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_user_name(context, values['name'])

        user = models.User()
        user.update(values)
        try:
            user.save()
        except db_exc.DBDuplicateEntry:
            raise exception.UserAlreadyExists(field='name',
                                                  value=values['name'])
        return user

    def get_user_by_uuid(self, context, user_uuid):
        query = model_query(models.User)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=user_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UserNotFound(user=user_uuid)

    def get_user_by_name(self, context, user_name):
        query = model_query(models.User)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=user_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UserNotFound(user=user_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple users exist with same '
                                     'name. Please use the user uuid '
                                     'instead.')

    def destroy_user(self, context, user_id):
        session = get_session()
        with session.begin():
            query = model_query(models.User, session=session)
            query = add_identity_filter(query, user_id)
            count = query.delete()
            if count != 1:
                raise exception.UserNotFound(user_id)

    def update_user(self, context, user_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing User.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_user_name(context, values['name'])

        return self._do_update_user(user_id, values)

    def _do_update_user(self, user_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.User, session=session)
            query = add_identity_filter(query, user_id)
            LOG.debug('_do_update_user xxxxxx user_id =%s, query=%s, values=%s',
                      user_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.UserNotFound(user=user_id)

            ref.update(values)
        return ref
    # provideraccount section
    def _add_provideraccounts_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_provideraccounts(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Provideraccount)
        # query = self._add_tenant_filters(context, query)
        query = self._add_provideraccounts_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_provideraccounts xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of provideraccounts is %s', (sort_key))
        return _paginate_query(models.Provideraccount, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_provideraccount_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Provideraccount). \
            filter(func.lower(models.Provideraccount.name) == lowername)
        provideraccount_with_same_name = base_query.count()
        if provideraccount_with_same_name > 0:
            raise exception.ProvideraccountAlreadyExists(field='name',
                                                  value=lowername)

    def create_provideraccount(self, context, values):
        # ensure defaults are present for new provideraccounts
        LOG.debug('sqlalchemy api.py create_provideraccount xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_provideraccount_name(context, values['name'])

        provideraccount = models.Provideraccount()
        provideraccount.update(values)
        try:
            provideraccount.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProvideraccountAlreadyExists(field='name',
                                                  value=values['name'])
        return provideraccount

    def get_provideraccount_by_uuid(self, context, provideraccount_uuid):
        query = model_query(models.Provideraccount)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=provideraccount_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvideraccountNotFound(provideraccount=provideraccount_uuid)

    def get_provideraccount_by_name(self, context, provideraccount_name):
        query = model_query(models.Provideraccount)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=provideraccount_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvideraccountNotFound(provideraccount=provideraccount_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple provideraccounts exist with same '
                                     'name. Please use the provideraccount uuid '
                                     'instead.')

    def destroy_provideraccount(self, context, provideraccount_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Provideraccount, session=session)
            query = add_identity_filter(query, provideraccount_id)
            count = query.delete()
            if count != 1:
                raise exception.ProvideraccountNotFound(provideraccount_id)

    def update_provideraccount(self, context, provideraccount_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Provideraccount.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_provideraccount_name(context, values['name'])

        return self._do_update_provideraccount(provideraccount_id, values)

    def _do_update_provideraccount(self, provideraccount_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Provideraccount, session=session)
            query = add_identity_filter(query, provideraccount_id)
            LOG.debug('_do_update_provideraccount xxxxxx provideraccount_id =%s, query=%s, values=%s',
                      provideraccount_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProvideraccountNotFound(provideraccount=provideraccount_id)

            ref.update(values)
        return ref
    # providervm section
    def _add_providervms_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_providervms(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Providervm)
        # query = self._add_tenant_filters(context, query)
        query = self._add_providervms_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_providervms xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of providervms is %s', (sort_key))
        return _paginate_query(models.Providervm, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_providervm_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Providervm). \
            filter(func.lower(models.Providervm.name) == lowername)
        providervm_with_same_name = base_query.count()
        if providervm_with_same_name > 0:
            raise exception.ProvidervmAlreadyExists(field='name',
                                                  value=lowername)

    def create_providervm(self, context, values):
        # ensure defaults are present for new providervms
        LOG.debug('sqlalchemy api.py create_providervm xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_providervm_name(context, values['name'])

        providervm = models.Providervm()
        providervm.update(values)
        try:
            providervm.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProvidervmAlreadyExists(field='name',
                                                  value=values['name'])
        return providervm

    def get_providervm_by_uuid(self, context, providervm_uuid):
        query = model_query(models.Providervm)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=providervm_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvidervmNotFound(providervm=providervm_uuid)

    def get_providervm_by_name(self, context, providervm_name):
        query = model_query(models.Providervm)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=providervm_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProvidervmNotFound(providervm=providervm_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple providervms exist with same '
                                     'name. Please use the providervm uuid '
                                     'instead.')

    def destroy_providervm(self, context, providervm_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Providervm, session=session)
            query = add_identity_filter(query, providervm_id)
            count = query.delete()
            if count != 1:
                raise exception.ProvidervmNotFound(providervm_id)

    def update_providervm(self, context, providervm_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Providervm.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_providervm_name(context, values['name'])

        return self._do_update_providervm(providervm_id, values)

    def _do_update_providervm(self, providervm_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Providervm, session=session)
            query = add_identity_filter(query, providervm_id)
            LOG.debug('_do_update_providervm xxxxxx providervm_id =%s, query=%s, values=%s',
                      providervm_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProvidervmNotFound(providervm=providervm_id)

            ref.update(values)
        return ref
    # instance section
    def _add_instances_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_instances(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Instance)
        # query = self._add_tenant_filters(context, query)
        query = self._add_instances_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_instances xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of instances is %s', (sort_key))
        return _paginate_query(models.Instance, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_instance_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Instance). \
            filter(func.lower(models.Instance.name) == lowername)
        instance_with_same_name = base_query.count()
        if instance_with_same_name > 0:
            raise exception.InstanceAlreadyExists(field='name',
                                                  value=lowername)

    def create_instance(self, context, values):
        # ensure defaults are present for new instances
        LOG.debug('sqlalchemy api.py create_instance xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_instance_name(context, values['name'])

        instance = models.Instance()
        instance.update(values)
        try:
            instance.save()
        except db_exc.DBDuplicateEntry:
            raise exception.InstanceAlreadyExists(field='name',
                                                  value=values['name'])
        return instance

    def get_instance_by_uuid(self, context, instance_uuid):
        query = model_query(models.Instance)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=instance_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstanceNotFound(instance=instance_uuid)

    def get_instance_by_name(self, context, instance_name):
        query = model_query(models.Instance)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=instance_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstanceNotFound(instance=instance_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple instances exist with same '
                                     'name. Please use the instance uuid '
                                     'instead.')

    def destroy_instance(self, context, instance_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Instance, session=session)
            query = add_identity_filter(query, instance_id)
            count = query.delete()
            if count != 1:
                raise exception.InstanceNotFound(instance_id)

    def update_instance(self, context, instance_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Instance.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_instance_name(context, values['name'])

        return self._do_update_instance(instance_id, values)

    def _do_update_instance(self, instance_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Instance, session=session)
            query = add_identity_filter(query, instance_id)
            LOG.debug('_do_update_instance xxxxxx instance_id =%s, query=%s, values=%s',
                      instance_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.InstanceNotFound(instance=instance_id)

            ref.update(values)
        return ref
    # storagerate section
    def _add_storagerates_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_storagerates(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Storagerate)
        # query = self._add_tenant_filters(context, query)
        query = self._add_storagerates_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_storagerates xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of storagerates is %s', (sort_key))
        return _paginate_query(models.Storagerate, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_storagerate_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Storagerate). \
            filter(func.lower(models.Storagerate.name) == lowername)
        storagerate_with_same_name = base_query.count()
        if storagerate_with_same_name > 0:
            raise exception.StoragerateAlreadyExists(field='name',
                                                  value=lowername)

    def create_storagerate(self, context, values):
        # ensure defaults are present for new storagerates
        LOG.debug('sqlalchemy api.py create_storagerate xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_storagerate_name(context, values['name'])

        storagerate = models.Storagerate()
        storagerate.update(values)
        try:
            storagerate.save()
        except db_exc.DBDuplicateEntry:
            raise exception.StoragerateAlreadyExists(field='name',
                                                  value=values['name'])
        return storagerate

    def get_storagerate_by_uuid(self, context, storagerate_uuid):
        query = model_query(models.Storagerate)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=storagerate_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StoragerateNotFound(storagerate=storagerate_uuid)

    def get_storagerate_by_name(self, context, storagerate_name):
        query = model_query(models.Storagerate)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=storagerate_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StoragerateNotFound(storagerate=storagerate_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple storagerates exist with same '
                                     'name. Please use the storagerate uuid '
                                     'instead.')

    def destroy_storagerate(self, context, storagerate_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Storagerate, session=session)
            query = add_identity_filter(query, storagerate_id)
            count = query.delete()
            if count != 1:
                raise exception.StoragerateNotFound(storagerate_id)

    def update_storagerate(self, context, storagerate_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Storagerate.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_storagerate_name(context, values['name'])

        return self._do_update_storagerate(storagerate_id, values)

    def _do_update_storagerate(self, storagerate_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Storagerate, session=session)
            query = add_identity_filter(query, storagerate_id)
            LOG.debug('_do_update_storagerate xxxxxx storagerate_id =%s, query=%s, values=%s',
                      storagerate_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.StoragerateNotFound(storagerate=storagerate_id)

            ref.update(values)
        return ref
    # provider section
    def _add_providers_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_providers(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Provider)
        # query = self._add_tenant_filters(context, query)
        query = self._add_providers_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_providers xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of providers is %s', (sort_key))
        return _paginate_query(models.Provider, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_provider_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Provider). \
            filter(func.lower(models.Provider.name) == lowername)
        provider_with_same_name = base_query.count()
        if provider_with_same_name > 0:
            raise exception.ProviderAlreadyExists(field='name',
                                                  value=lowername)

    def create_provider(self, context, values):
        # ensure defaults are present for new providers
        LOG.debug('sqlalchemy api.py create_provider xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_provider_name(context, values['name'])

        provider = models.Provider()
        provider.update(values)
        try:
            provider.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProviderAlreadyExists(field='name',
                                                  value=values['name'])
        return provider

    def get_provider_by_uuid(self, context, provider_uuid):
        query = model_query(models.Provider)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=provider_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderNotFound(provider=provider_uuid)

    def get_provider_by_name(self, context, provider_name):
        query = model_query(models.Provider)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=provider_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderNotFound(provider=provider_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple providers exist with same '
                                     'name. Please use the provider uuid '
                                     'instead.')

    def destroy_provider(self, context, provider_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Provider, session=session)
            query = add_identity_filter(query, provider_id)
            count = query.delete()
            if count != 1:
                raise exception.ProviderNotFound(provider_id)

    def update_provider(self, context, provider_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Provider.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_provider_name(context, values['name'])

        return self._do_update_provider(provider_id, values)

    def _do_update_provider(self, provider_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Provider, session=session)
            query = add_identity_filter(query, provider_id)
            LOG.debug('_do_update_provider xxxxxx provider_id =%s, query=%s, values=%s',
                      provider_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProviderNotFound(provider=provider_id)

            ref.update(values)
        return ref
    # providerregion section
    def _add_providerregions_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_providerregions(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Providerregion)
        # query = self._add_tenant_filters(context, query)
        query = self._add_providerregions_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_providerregions xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of providerregions is %s', (sort_key))
        return _paginate_query(models.Providerregion, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_providerregion_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Providerregion). \
            filter(func.lower(models.Providerregion.name) == lowername)
        providerregion_with_same_name = base_query.count()
        if providerregion_with_same_name > 0:
            raise exception.ProviderregionAlreadyExists(field='name',
                                                  value=lowername)

    def create_providerregion(self, context, values):
        # ensure defaults are present for new providerregions
        LOG.debug('sqlalchemy api.py create_providerregion xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_providerregion_name(context, values['name'])

        providerregion = models.Providerregion()
        providerregion.update(values)
        try:
            providerregion.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ProviderregionAlreadyExists(field='name',
                                                  value=values['name'])
        return providerregion

    def get_providerregion_by_uuid(self, context, providerregion_uuid):
        query = model_query(models.Providerregion)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=providerregion_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderregionNotFound(providerregion=providerregion_uuid)

    def get_providerregion_by_name(self, context, providerregion_name):
        query = model_query(models.Providerregion)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=providerregion_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ProviderregionNotFound(providerregion=providerregion_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple providerregions exist with same '
                                     'name. Please use the providerregion uuid '
                                     'instead.')

    def destroy_providerregion(self, context, providerregion_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Providerregion, session=session)
            query = add_identity_filter(query, providerregion_id)
            count = query.delete()
            if count != 1:
                raise exception.ProviderregionNotFound(providerregion_id)

    def update_providerregion(self, context, providerregion_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Providerregion.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_providerregion_name(context, values['name'])

        return self._do_update_providerregion(providerregion_id, values)

    def _do_update_providerregion(self, providerregion_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Providerregion, session=session)
            query = add_identity_filter(query, providerregion_id)
            LOG.debug('_do_update_providerregion xxxxxx providerregion_id =%s, query=%s, values=%s',
                      providerregion_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ProviderregionNotFound(providerregion=providerregion_id)

            ref.update(values)
        return ref
    # instancetype section
    def _add_instancetypes_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_instancetypes(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Instancetype)
        # query = self._add_tenant_filters(context, query)
        query = self._add_instancetypes_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_instancetypes xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of instancetypes is %s', (sort_key))
        return _paginate_query(models.Instancetype, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_instancetype_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Instancetype). \
            filter(func.lower(models.Instancetype.name) == lowername)
        instancetype_with_same_name = base_query.count()
        if instancetype_with_same_name > 0:
            raise exception.InstancetypeAlreadyExists(field='name',
                                                  value=lowername)

    def create_instancetype(self, context, values):
        # ensure defaults are present for new instancetypes
        LOG.debug('sqlalchemy api.py create_instancetype xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_instancetype_name(context, values['name'])

        instancetype = models.Instancetype()
        instancetype.update(values)
        try:
            instancetype.save()
        except db_exc.DBDuplicateEntry:
            raise exception.InstancetypeAlreadyExists(field='name',
                                                  value=values['name'])
        return instancetype

    def get_instancetype_by_uuid(self, context, instancetype_uuid):
        query = model_query(models.Instancetype)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=instancetype_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstancetypeNotFound(instancetype=instancetype_uuid)

    def get_instancetype_by_name(self, context, instancetype_name):
        query = model_query(models.Instancetype)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=instancetype_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.InstancetypeNotFound(instancetype=instancetype_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple instancetypes exist with same '
                                     'name. Please use the instancetype uuid '
                                     'instead.')

    def destroy_instancetype(self, context, instancetype_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Instancetype, session=session)
            query = add_identity_filter(query, instancetype_id)
            count = query.delete()
            if count != 1:
                raise exception.InstancetypeNotFound(instancetype_id)

    def update_instancetype(self, context, instancetype_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Instancetype.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_instancetype_name(context, values['name'])

        return self._do_update_instancetype(instancetype_id, values)

    def _do_update_instancetype(self, instancetype_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Instancetype, session=session)
            query = add_identity_filter(query, instancetype_id)
            LOG.debug('_do_update_instancetype xxxxxx instancetype_id =%s, query=%s, values=%s',
                      instancetype_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.InstancetypeNotFound(instancetype=instancetype_id)

            ref.update(values)
        return ref
    # usage section
    def _add_usages_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_usages(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Usage)
        # query = self._add_tenant_filters(context, query)
        query = self._add_usages_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_usages xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of usages is %s', (sort_key))
        return _paginate_query(models.Usage, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_usage_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Usage). \
            filter(func.lower(models.Usage.name) == lowername)
        usage_with_same_name = base_query.count()
        if usage_with_same_name > 0:
            raise exception.UsageAlreadyExists(field='name',
                                                  value=lowername)

    def create_usage(self, context, values):
        # ensure defaults are present for new usages
        LOG.debug('sqlalchemy api.py create_usage xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_usage_name(context, values['name'])

        usage = models.Usage()
        usage.update(values)
        try:
            usage.save()
        except db_exc.DBDuplicateEntry:
            raise exception.UsageAlreadyExists(field='name',
                                                  value=values['name'])
        return usage

    def get_usage_by_uuid(self, context, usage_uuid):
        query = model_query(models.Usage)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=usage_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UsageNotFound(usage=usage_uuid)

    def get_usage_by_name(self, context, usage_name):
        query = model_query(models.Usage)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=usage_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.UsageNotFound(usage=usage_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple usages exist with same '
                                     'name. Please use the usage uuid '
                                     'instead.')

    def destroy_usage(self, context, usage_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Usage, session=session)
            query = add_identity_filter(query, usage_id)
            count = query.delete()
            if count != 1:
                raise exception.UsageNotFound(usage_id)

    def update_usage(self, context, usage_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Usage.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_usage_name(context, values['name'])

        return self._do_update_usage(usage_id, values)

    def _do_update_usage(self, usage_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Usage, session=session)
            query = add_identity_filter(query, usage_id)
            LOG.debug('_do_update_usage xxxxxx usage_id =%s, query=%s, values=%s',
                      usage_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.UsageNotFound(usage=usage_id)

            ref.update(values)
        return ref
    # statement section
    def _add_statements_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_statements(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Statement)
        # query = self._add_tenant_filters(context, query)
        query = self._add_statements_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_statements xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of statements is %s', (sort_key))
        return _paginate_query(models.Statement, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_statement_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Statement). \
            filter(func.lower(models.Statement.name) == lowername)
        statement_with_same_name = base_query.count()
        if statement_with_same_name > 0:
            raise exception.StatementAlreadyExists(field='name',
                                                  value=lowername)

    def create_statement(self, context, values):
        # ensure defaults are present for new statements
        LOG.debug('sqlalchemy api.py create_statement xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_statement_name(context, values['name'])

        statement = models.Statement()
        statement.update(values)
        try:
            statement.save()
        except db_exc.DBDuplicateEntry:
            raise exception.StatementAlreadyExists(field='name',
                                                  value=values['name'])
        return statement

    def get_statement_by_uuid(self, context, statement_uuid):
        query = model_query(models.Statement)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=statement_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StatementNotFound(statement=statement_uuid)

    def get_statement_by_name(self, context, statement_name):
        query = model_query(models.Statement)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=statement_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.StatementNotFound(statement=statement_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple statements exist with same '
                                     'name. Please use the statement uuid '
                                     'instead.')

    def destroy_statement(self, context, statement_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Statement, session=session)
            query = add_identity_filter(query, statement_id)
            count = query.delete()
            if count != 1:
                raise exception.StatementNotFound(statement_id)

    def update_statement(self, context, statement_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Statement.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_statement_name(context, values['name'])

        return self._do_update_statement(statement_id, values)

    def _do_update_statement(self, statement_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Statement, session=session)
            query = add_identity_filter(query, statement_id)
            LOG.debug('_do_update_statement xxxxxx statement_id =%s, query=%s, values=%s',
                      statement_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.StatementNotFound(statement=statement_id)

            ref.update(values)
        return ref
    # computerate section
    def _add_computerates_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_computerates(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Computerate)
        # query = self._add_tenant_filters(context, query)
        query = self._add_computerates_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_computerates xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of computerates is %s', (sort_key))
        return _paginate_query(models.Computerate, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_computerate_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Computerate). \
            filter(func.lower(models.Computerate.name) == lowername)
        computerate_with_same_name = base_query.count()
        if computerate_with_same_name > 0:
            raise exception.ComputerateAlreadyExists(field='name',
                                                  value=lowername)

    def create_computerate(self, context, values):
        # ensure defaults are present for new computerates
        LOG.debug('sqlalchemy api.py create_computerate xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_computerate_name(context, values['name'])

        computerate = models.Computerate()
        computerate.update(values)
        try:
            computerate.save()
        except db_exc.DBDuplicateEntry:
            raise exception.ComputerateAlreadyExists(field='name',
                                                  value=values['name'])
        return computerate

    def get_computerate_by_uuid(self, context, computerate_uuid):
        query = model_query(models.Computerate)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=computerate_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputerateNotFound(computerate=computerate_uuid)

    def get_computerate_by_name(self, context, computerate_name):
        query = model_query(models.Computerate)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=computerate_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.ComputerateNotFound(computerate=computerate_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple computerates exist with same '
                                     'name. Please use the computerate uuid '
                                     'instead.')

    def destroy_computerate(self, context, computerate_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Computerate, session=session)
            query = add_identity_filter(query, computerate_id)
            count = query.delete()
            if count != 1:
                raise exception.ComputerateNotFound(computerate_id)

    def update_computerate(self, context, computerate_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Computerate.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_computerate_name(context, values['name'])

        return self._do_update_computerate(computerate_id, values)

    def _do_update_computerate(self, computerate_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Computerate, session=session)
            query = add_identity_filter(query, computerate_id)
            LOG.debug('_do_update_computerate xxxxxx computerate_id =%s, query=%s, values=%s',
                      computerate_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.ComputerateNotFound(computerate=computerate_id)

            ref.update(values)
        return ref
    # payment section
    def _add_payments_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_payments(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Payment)
        # query = self._add_tenant_filters(context, query)
        query = self._add_payments_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_payments xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of payments is %s', (sort_key))
        return _paginate_query(models.Payment, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_payment_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Payment). \
            filter(func.lower(models.Payment.name) == lowername)
        payment_with_same_name = base_query.count()
        if payment_with_same_name > 0:
            raise exception.PaymentAlreadyExists(field='name',
                                                  value=lowername)

    def create_payment(self, context, values):
        # ensure defaults are present for new payments
        LOG.debug('sqlalchemy api.py create_payment xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_payment_name(context, values['name'])

        payment = models.Payment()
        payment.update(values)
        try:
            payment.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PaymentAlreadyExists(field='name',
                                                  value=values['name'])
        return payment

    def get_payment_by_uuid(self, context, payment_uuid):
        query = model_query(models.Payment)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=payment_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentNotFound(payment=payment_uuid)

    def get_payment_by_name(self, context, payment_name):
        query = model_query(models.Payment)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=payment_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentNotFound(payment=payment_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple payments exist with same '
                                     'name. Please use the payment uuid '
                                     'instead.')

    def destroy_payment(self, context, payment_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Payment, session=session)
            query = add_identity_filter(query, payment_id)
            count = query.delete()
            if count != 1:
                raise exception.PaymentNotFound(payment_id)

    def update_payment(self, context, payment_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Payment.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_payment_name(context, values['name'])

        return self._do_update_payment(payment_id, values)

    def _do_update_payment(self, payment_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Payment, session=session)
            query = add_identity_filter(query, payment_id)
            LOG.debug('_do_update_payment xxxxxx payment_id =%s, query=%s, values=%s',
                      payment_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.PaymentNotFound(payment=payment_id)

            ref.update(values)
        return ref
    # paymentmethod section
    def _add_paymentmethods_filters(self, query, filters):
        if filters is None:
            filters = {}

        filter_names = ['name', 'status']
        for name in filter_names:
            if name in filters:
                query = query.filter_by(**{name: filters[name]})

        return query

    def list_paymentmethods(self, context, filters=None, limit=None,
                       marker=None, sort_key=None, sort_dir=None):
        query = model_query(models.Paymentmethod)
        # query = self._add_tenant_filters(context, query)
        query = self._add_paymentmethods_filters(query, filters)
        LOG.debug('sqlalchemy api.py list_paymentmethods xxx query=%s, xxx', (query))
        LOG.debug('The sort_key of paymentmethods is %s', (sort_key))
        return _paginate_query(models.Paymentmethod, limit, marker,
                               sort_key, sort_dir, query)

    def _validate_unique_paymentmethod_name(self, context, name):
        lowername = name.lower()
        base_query = model_query(models.Paymentmethod). \
            filter(func.lower(models.Paymentmethod.name) == lowername)
        paymentmethod_with_same_name = base_query.count()
        if paymentmethod_with_same_name > 0:
            raise exception.PaymentmethodAlreadyExists(field='name',
                                                  value=lowername)

    def create_paymentmethod(self, context, values):
        # ensure defaults are present for new paymentmethods
        LOG.debug('sqlalchemy api.py create_paymentmethod xxx values=%s' % (values))
        if not values.get('uuid'):
            values['uuid'] = uuidutils.generate_uuid()

        if values.get('name'):
            self._validate_unique_paymentmethod_name(context, values['name'])

        paymentmethod = models.Paymentmethod()
        paymentmethod.update(values)
        try:
            paymentmethod.save()
        except db_exc.DBDuplicateEntry:
            raise exception.PaymentmethodAlreadyExists(field='name',
                                                  value=values['name'])
        return paymentmethod

    def get_paymentmethod_by_uuid(self, context, paymentmethod_uuid):
        query = model_query(models.Paymentmethod)
        # query = self._add_tenant_filters(context, query)
        query = query.filter_by(uuid=paymentmethod_uuid)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentmethodNotFound(paymentmethod=paymentmethod_uuid)

    def get_paymentmethod_by_name(self, context, paymentmethod_name):
        query = model_query(models.Paymentmethod)
        query = self._add_tenant_filters(context, query)
        query = query.filter_by(name=paymentmethod_name)
        try:
            return query.one()
        except NoResultFound:
            raise exception.PaymentmethodNotFound(paymentmethod=paymentmethod_name)
        except MultipleResultsFound:
            raise exception.Conflict('Multiple paymentmethods exist with same '
                                     'name. Please use the paymentmethod uuid '
                                     'instead.')

    def destroy_paymentmethod(self, context, paymentmethod_id):
        session = get_session()
        with session.begin():
            query = model_query(models.Paymentmethod, session=session)
            query = add_identity_filter(query, paymentmethod_id)
            count = query.delete()
            if count != 1:
                raise exception.PaymentmethodNotFound(paymentmethod_id)

    def update_paymentmethod(self, context, paymentmethod_id, values):
        # NOTE(dtantsur): this can lead to very strange errors
        if 'uuid' in values:
            msg = _("Cannot overwrite UUID for an existing Paymentmethod.")
            raise exception.InvalidParameterValue(err=msg)

        if 'name' in values:
            self._validate_unique_paymentmethod_name(context, values['name'])

        return self._do_update_paymentmethod(paymentmethod_id, values)

    def _do_update_paymentmethod(self, paymentmethod_id, values):
        session = get_session()
        with session.begin():
            query = model_query(models.Paymentmethod, session=session)
            query = add_identity_filter(query, paymentmethod_id)
            LOG.debug('_do_update_paymentmethod xxxxxx paymentmethod_id =%s, query=%s, values=%s',
                      paymentmethod_id, query, values)
            try:
                ref = query.with_lockmode('update').one()
            except NoResultFound:
                raise exception.PaymentmethodNotFound(paymentmethod=paymentmethod_id)

            ref.update(values)
        return ref
