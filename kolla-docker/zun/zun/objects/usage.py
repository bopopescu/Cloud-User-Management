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
class Usage(base.ZunPersistentObject, base.ZunObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'user_id': fields.StringField(nullable=True),
        'instance_id': fields.StringField(nullable=True),
        'uuid': fields.UUIDField(nullable=True),
        'compute_rate_id': fields.StringField(nullable=True),
        'storage_rate_id': fields.StringField(nullable=True),
        'start_time': fields.DateTimeField(nullable=True),
        'stop_time': fields.DateTimeField(nullable=True),
        'duration': fields.IntegerField(nullable=True),
        'cost': fields.FloatField(nullable=True),
        'displayname': fields.StringField(nullable=True),
        'displayname2': fields.StringField(nullable=True),
        'displayname3': fields.StringField(nullable=True),
        'displayname4': fields.StringField(nullable=True)
    }

    @staticmethod
    def _from_db_object(usage, db_usage):
        """Converts a database entity to a formal object."""
        for field in usage.fields:
            setattr(usage, field, db_usage[field])

        usage.obj_reset_changes()
        return usage

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [Usage._from_db_object(cls(context), obj)
                for obj in db_objects]

    @base.remotable_classmethod
    def get_by_uuid(cls, context, uuid):
        """Find a usage based on uuid and return a :class:`Usage` object.

        :param uuid: the uuid of a usage.
        :param context: Security context
        :returns: a :class:`Usage` object.
        """
        db_usage = dbapi.get_usage_by_uuid(context, uuid)
        usage = Usage._from_db_object(cls(context), db_usage)
        return usage

    @base.remotable_classmethod
    def get_by_name(cls, context, name):
        """Find a usage based on name and return a Usage object.

        :param name: the logical name of a usage.
        :param context: Security context
        :returns: a :class:`Usage` object.
        """
        db_usage = dbapi.get_usage_by_name(context, name)
        usage = Usage._from_db_object(cls(context), db_usage)
        return usage

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None,
             sort_key=None, sort_dir=None, filters=None):
        """Return a list of Usage objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param filters: filters when list usages, the filter name could be
                        'name', 'image', 'project_id', 'user_id', 'memory'.
                        For example, filters={'image': 'nginx'}
        :returns: a list of :class:`Usage` object.

        """
        db_usages = dbapi.list_usages(
            context, limit=limit, marker=marker, sort_key=sort_key,
            sort_dir=sort_dir, filters=filters)
        LOG.debug('get_all Usage LISt Usage xxxxxx db_usages =%s.',db_usages)
        return Usage._from_db_object_list(db_usages, cls, context)

    @base.remotable_classmethod
    def list_by_host(cls, context, host):
        """Return a list of Usage objects by host.

        :param context: Security context.
        :param host: A compute host.
        :returns: a list of :class:`Usage` object.

        """
        db_usages = dbapi.list_usages(context, filters={'host': host})
        return Usage._from_db_object_list(db_usages, cls, context)

    @base.remotable
    def create(self, context):
        """Create a Usage record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Usage(context)

        """
        values = self.obj_get_changes()
        db_usage = dbapi.create_usage(context, values)
        self._from_db_object(self, db_usage)

    @base.remotable
    def destroy(self, context=None):
        """Delete the Usage from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Usage(context)
        """
        dbapi.destroy_usage(context, self.uuid)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this Usage.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Usage(context)
        """
        updates = self.obj_get_changes()
        LOG.debug('Save Usage xxxxxx uuid =%s, updates=%s', self.uuid, updates)
        dbapi.update_usage(context, self.uuid, updates)

        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads updates for this Usage.

        Loads a usage with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded usage column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: Usage(context)
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
