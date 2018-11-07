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

from oslo_versionedobjects import fields

from zun.db import api as dbapi
from zun.objects import base
from zun.objects import fields as z_fields
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


@base.ZunObjectRegistry.register
class Provider(base.ZunPersistentObject, base.ZunObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'provider': fields.StringField(nullable=True),
        'uuid': fields.UUIDField(nullable=True),
    }

    @staticmethod
    def _from_db_object(provider, db_provider):
        """Converts a database entity to a formal object."""
        for field in provider.fields:
            setattr(provider, field, db_provider[field])

        provider.obj_reset_changes()
        return provider

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [Provider._from_db_object(cls(context), obj)
                for obj in db_objects]

    @base.remotable_classmethod
    def get_by_uuid(cls, context, uuid):
        """Find a provider based on uuid and return a :class:`Provider` object.

        :param uuid: the uuid of a provider.
        :param context: Security context
        :returns: a :class:`Provider` object.
        """
        db_provider = dbapi.get_provider_by_uuid(context, uuid)
        provider = Provider._from_db_object(cls(context), db_provider)
        return provider

    @base.remotable_classmethod
    def get_by_name(cls, context, name):
        """Find a provider based on name and return a Provider object.

        :param name: the logical name of a provider.
        :param context: Security context
        :returns: a :class:`Provider` object.
        """
        db_provider = dbapi.get_provider_by_name(context, name)
        provider = Provider._from_db_object(cls(context), db_provider)
        return provider

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None,
             sort_key=None, sort_dir=None, filters=None):
        """Return a list of Provider objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param filters: filters when list providers, the filter name could be
                        'name', 'image', 'project_id', 'user_id', 'memory'.
                        For example, filters={'image': 'nginx'}
        :returns: a list of :class:`Provider` object.

        """
        db_providers = dbapi.list_providers(
            context, limit=limit, marker=marker, sort_key=sort_key,
            sort_dir=sort_dir, filters=filters)
        LOG.debug('get_all Provider LISt Provider xxxxxx db_providers =%s.',db_providers)
        return Provider._from_db_object_list(db_providers, cls, context)

    @base.remotable_classmethod
    def list_by_host(cls, context, host):
        """Return a list of Provider objects by host.

        :param context: Security context.
        :param host: A compute host.
        :returns: a list of :class:`Provider` object.

        """
        db_providers = dbapi.list_providers(context, filters={'host': host})
        return Provider._from_db_object_list(db_providers, cls, context)

    @base.remotable
    def create(self, context):
        """Create a Provider record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Provider(context)

        """
        values = self.obj_get_changes()
        db_provider = dbapi.create_provider(context, values)
        self._from_db_object(self, db_provider)

    @base.remotable
    def destroy(self, context=None):
        """Delete the Provider from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Provider(context)
        """
        dbapi.destroy_provider(context, self.uuid)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this Provider.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Provider(context)
        """
        updates = self.obj_get_changes()
        LOG.debug('Save Provider xxxxxx uuid =%s, updates=%s', self.uuid, updates)
        dbapi.update_provider(context, self.uuid, updates)

        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads updates for this Provider.

        Loads a provider with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded provider column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Provider(context)
        """
        current = self.__class__.get_by_uuid(self._context, uuid=self.uuid)
        for field in self.fields:
            if self.obj_attr_is_set(field) and \
               getattr(self, field) != getattr(current, field):
                setattr(self, field, getattr(current, field))

    def get_sandbox_id(self):
        if self.meta:
            return self.meta.get('sandbox_id', None)
        else:
            return None

    def set_sandbox_id(self, sandbox_id):
        if self.meta is None:
            self.meta = {'sandbox_id': sandbox_id}
        else:
            self.meta['sandbox_id'] = sandbox_id
