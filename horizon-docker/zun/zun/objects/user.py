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
class User(base.ZunPersistentObject, base.ZunObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(),
        'user_name': fields.StringField(nullable=True),
        'last_name': fields.StringField(nullable=True),
        'uuid': fields.UUIDField(nullable=True),
        'first_name': fields.StringField(nullable=True),
        'middle_name': fields.StringField(nullable=True),
        'password': fields.StringField(nullable=True),
        'account_status': fields.IntegerField(nullable=True),
        'failed_attempt': fields.IntegerField(nullable=True),
        'last_login_method': fields.IntegerField(nullable=True),
        'current_user_charge_tier': fields.IntegerField(nullable=True),
        'admin_ind': fields.IntegerField(nullable=True)
    }

    @staticmethod
    def _from_db_object(user, db_user):
        """Converts a database entity to a formal object."""
        for field in user.fields:
            setattr(user, field, db_user[field])

        user.obj_reset_changes()
        return user

    @staticmethod
    def _from_db_object_list(db_objects, cls, context):
        """Converts a list of database entities to a list of formal objects."""
        return [User._from_db_object(cls(context), obj)
                for obj in db_objects]

    @base.remotable_classmethod
    def get_by_uuid(cls, context, uuid):
        """Find a user based on uuid and return a :class:`User` object.

        :param uuid: the uuid of a user.
        :param context: Security context
        :returns: a :class:`User` object.
        """
        db_user = dbapi.get_user_by_uuid(context, uuid)
        user = User._from_db_object(cls(context), db_user)
        return user

    @base.remotable_classmethod
    def get_by_name(cls, context, name):
        """Find a user based on name and return a User object.

        :param name: the logical name of a user.
        :param context: Security context
        :returns: a :class:`User` object.
        """
        db_user = dbapi.get_user_by_name(context, name)
        user = User._from_db_object(cls(context), db_user)
        return user

    @base.remotable_classmethod
    def list(cls, context, limit=None, marker=None,
             sort_key=None, sort_dir=None, filters=None):
        """Return a list of User objects.

        :param context: Security context.
        :param limit: maximum number of resources to return in a single result.
        :param marker: pagination marker for large data sets.
        :param sort_key: column to sort results by.
        :param sort_dir: direction to sort. "asc" or "desc".
        :param filters: filters when list users, the filter name could be
                        'name', 'image', 'project_id', 'user_id', 'memory'.
                        For example, filters={'image': 'nginx'}
        :returns: a list of :class:`User` object.

        """
        db_users = dbapi.list_users(
            context, limit=limit, marker=marker, sort_key=sort_key,
            sort_dir=sort_dir, filters=filters)
        LOG.debug('get_all User LISt User xxxxxx db_users =%s.',db_users)
        return User._from_db_object_list(db_users, cls, context)

    @base.remotable_classmethod
    def list_by_host(cls, context, host):
        """Return a list of User objects by host.

        :param context: Security context.
        :param host: A compute host.
        :returns: a list of :class:`User` object.

        """
        db_users = dbapi.list_users(context, filters={'host': host})
        return User._from_db_object_list(db_users, cls, context)

    @base.remotable
    def create(self, context):
        """Create a User record in the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: User(context)

        """
        values = self.obj_get_changes()
        db_user = dbapi.create_user(context, values)
        self._from_db_object(self, db_user)

    @base.remotable
    def destroy(self, context=None):
        """Delete the User from the DB.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: User(context)
        """
        dbapi.destroy_user(context, self.uuid)
        self.obj_reset_changes()

    @base.remotable
    def save(self, context=None):
        """Save updates to this User.

        Updates will be made column by column based on the result
        of self.what_changed().

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: User(context)
        """
        updates = self.obj_get_changes()
        LOG.debug('Save User xxxxxx uuid =%s, updates=%s', self.uuid, updates)
        dbapi.update_user(context, self.uuid, updates)

        self.obj_reset_changes()

    @base.remotable
    def refresh(self, context=None):
        """Loads updates for this User.

        Loads a user with the same uuid from the database and
        checks for updated attributes. Updates are applied from
        the loaded user column by column, if there are any updates.

        :param context: Security context. NOTE: This should only
                        be used internally by the indirection_api.
                        Unfortunately, RPC requires context as the first
                        argument, even though we don't use it.
                        A context should be set when instantiating the
                        object, e.g.: User(context)
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
