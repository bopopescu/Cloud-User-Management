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

from django.views import generic

from zun_ui.api import client
import logging
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils
LOG = logging.getLogger(__name__)

def change_to_id(obj):
    """Change key named 'uuid' to 'id'

    Zun returns objects with a field called 'uuid' many of Horizons
    directives however expect objects to have a field called 'id'.
    """
    obj['id'] = obj.pop('uuid')
    return obj



@urls.register
class Instancetype(generic.View):
    """API for retrieving a single container"""
    url_regex = r'zun/instancetypes/(?P<id>[^/]+)$'

    @rest_utils.ajax()
    def get(self, request, id):
        LOG.debug('restapi Instancetype xxxxxx get=%s, id=%s xxx' % (request, id))
        """Get a specific container"""
        return change_to_id(client.instancetype_show(request, id).to_dict())

    @rest_utils.ajax(data_required=True)
    def delete(self, request, id):
        """Delete single Container forcely by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        return client.instancetype_delete(request, id, force=True)

    @rest_utils.ajax(data_required=True)
    def patch(self, request, id):
        """Update a Container.

        Returns the Container object on success.
        """
        args = client.instancetype_update(request, id, **request.DATA)
        LOG.debug('restapi inside patch Instancetype xxxxxx args=%s, xxx' % (args))
        return args



@urls.register
class Instancetypes(generic.View):
    """API for Zun Containers"""
    url_regex = r'zun/instancetypes/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get a list of the Containers for a project.

        The returned result is an object with property 'items' and each
        item under this is a Container.
        """
        result = client.instancetype_list(request)
        LOG.debug('restapi Get yyyzzxxxxxx result= %s xxxxxx' % (result))
        return {'items': [change_to_id(n.to_dict()) for n in result]}

    @rest_utils.ajax(data_required=True)
    def delete(self, request):
        """Delete one or more Containers by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        for id in request.DATA:
            client.instancetype_delete(request, id)

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Create a new Container.

        Returns the new Container object on success.
        If 'run' attribute is set true, do 'run' instead 'create'
        """
        LOG.debug('instancetypes restapi POST xxxxxx %s xxxxx %s xxx' % (request, request.DATA))
        new_container = client.instancetype_create(request, **request.DATA)
        LOG.debug('zunclient post "%s" and url"%s"' % (new_container.uuid, new_container.to_dict()))
        return rest_utils.CreatedResponse(
            '/api/zun/instancetype/%s' % new_container.uuid,
            new_container.to_dict())
