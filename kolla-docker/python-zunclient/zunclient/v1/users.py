# Copyright 2014 NEC Corporation.  All rights reserved.
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

from six.moves.urllib import parse

from zunclient.common import base
from zunclient.common import utils
from zunclient import exceptions
import logging
LOG = logging.getLogger(__name__)

CREATION_ATTRIBUTES = ['id', 'user_name', 'last_name', 'first_name', 'middle_name', 'password', 'uuid',
                       'account_status', 'failed_attempt', 'last_login_method', 'current_user_charge_tier', 'admin_ind', 'displayname',
                       'passreset_url', 'activation_url', 'activation_expir_date', 'passreset_expir_date',
                       'last_login_time', 'last_success_login_ip', 'last_failed_login_ip',

                       'name', 'image', 'command', 'cpu', 'memory',
                       'environment', 'workdir', 'labels', 'image_pull_policy',
                       'restart_policy', 'interactive', 'image_driver',
                       'security_groups', 'hints', 'nets', 'auto_remove'
                       'carrier', 'carrier_name', 'carrier_access_key', 'carrier_access_key_id']

class User(base.Resource):
    def __repr__(self):
        return "<User %s>" % self._info


class ContainerManager(base.Manager):
    resource_class = User

    @staticmethod
    def _path(id=None):

        if id:
            return '/v1/users/%s' % id
        else:
            return '/v1/users'

    def list(self, marker=None, limit=None, sort_key=None,
             sort_dir=None, detail=False, all_tenants=False):
        """Retrieve a list of containers.

        :param all_tenants: Optional, list containers in all tenants

        :param marker: Optional, the UUID of a containers, eg the last
                       containers from a previous result set. Return
                       the next result set.
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of containers to return.
            2) limit == 0, return the entire list of containers.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the ZUN API
               (see Zun's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about containers.

        :returns: A list of containers.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(marker, limit, sort_key,
                                       sort_dir, all_tenants)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        LOG.debug('zunclient user user path=%s,  xxx list args xxx yyyy zzzzzzzzzzz', self._path(path))
        if limit is None:
            return self._list(self._path(path),
                              "users")
        else:
            return self._list_pagination(self._path(path),
                                         "users",
                                         limit=limit)

    def get(self, id, **kwargs):
        try:
            LOG.debug('zunclient xxx get path=%s,  kwargs=%s, zzzz', self._path(id), kwargs)
            return self._list(self._path(id),
                              qparams=kwargs)[0]
        except IndexError:
            return None

    '''def get_by_email(self, name, **kwargs):
        try:
            LOG.debug('zunclient xxx get path=%s,  kwargs=%s, zzzz', self._path(name), kwargs)
            return self._list(self._path(name),
                              qparams=kwargs)[0]
        except IndexError:
            return None'''

    def create(self, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exceptions.InvalidAttribute(
                    "Key must be in %s" % ','.join(CREATION_ATTRIBUTES))
        LOG.debug('zunclient create args xxx %s, %s, %s' % (self._path(), new, kwargs))
        return self._create(self._path(), new)

    def delete(self, id, **kwargs):
        return self._delete(self._path(id),
                            qparams=kwargs)

    def _action(self, id, action, method='POST', qparams=None, **kwargs):
        if qparams:
            action = "%s?%s" % (action,
                                parse.urlencode(qparams))
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Length', '0')
        resp, body = self.api.json_request(method,
                                           self._path(id) + action,
                                           **kwargs)
        return resp, body

    def start(self, id):
        return self._action(id, '/start')

    def stop(self, id, timeout):
        return self._action(id, '/stop',
                            qparams={'timeout': timeout})

    def restart(self, id, timeout):
        return self._action(id, '/reboot',
                            qparams={'timeout': timeout})

    def pause(self, id):
        return self._action(id, '/pause')

    def unpause(self, id):
        return self._action(id, '/unpause')

    def logs(self, id, **kwargs):
        if kwargs['stdout'] is False and kwargs['stderr'] is False:
            kwargs['stdout'] = True
            kwargs['stderr'] = True
        return self._action(id, '/logs', method='GET',
                            qparams=kwargs)[1]

    def execute(self, id, **kwargs):
        return self._action(id, '/execute',
                            qparams=kwargs)[1]

    def execute_resize(self, id, exec_id, width, height):
        self._action(id, '/execute_resize',
                     qparams={'exec_id': exec_id, 'w': width, 'h': height})[1]

    def kill(self, id, signal=None):
        return self._action(id, '/kill',
                            qparams={'signal': signal})[1]

    def run(self, **kwargs):
        if not set(kwargs).issubset(CREATION_ATTRIBUTES):
            raise exceptions.InvalidAttribute(
                "Key must be in %s" % ','.join(CREATION_ATTRIBUTES))
        else:
            return self._create(self._path() + '?run=true', kwargs)

    def rename(self, id, name):
        return self._action(id, '/rename',
                            qparams={'name': name})

    def update(self, id, **patch):
        LOG.debug('zunclient start update xxx path=%s, patch=%s' % (self._path(id), patch))
        return self._update(self._path(id), patch)

    def attach(self, id):
        return self._action(id, '/attach', method='GET')[1]

    def resize(self, id, width, height):
        return self._action(id, '/resize',
                            qparams={'w': width, 'h': height})[1]

    def top(self, id, ps_args=None):
        return self._action(id, '/top', method='GET',
                            qparams={'ps_args': ps_args})[1]

    def get_archive(self, id, path):
        return self._action(id, '/get_archive', method='GET',
                            qparams={'path': path})[1]

    def put_archive(self, id, path, data):
        return self._action(id, '/put_archive',
                            qparams={'path': path},
                            body={'data': data})

    def stats(self, id):
        return self._action(id, '/stats', method='GET')[1]

    def commit(self, id, repository, tag=None):
        if tag is not None:
            return self._action(id, '/commit', qparams={
                                'repository': repository, 'tag': tag})[1]
        else:
            return self._action(id, '/commit', qparams={
                                'repository': repository})[1]

    def add_security_group(self, id, security_group):
        return self._action(id, '/add_security_group',
                            qparams={'name': security_group})

    def network_detach(self, container, network):
        return self._action(container, '/network_detach',
                            qparams={'network': network})
