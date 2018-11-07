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
class User(generic.View):
    """API for retrieving a single container"""
    url_regex = r'zun/users/(?P<id>[^/]+)$'

    @rest_utils.ajax()
    def get(self, request, id):
        LOG.debug('restapi User xxxxxx get=%s, id=%s xxx' % (request, id))
        """Get a specific container"""
        return change_to_id(client.user_show(request, id).to_dict())

    @rest_utils.ajax(data_required=True)
    def delete(self, request, id):
        """Delete single Container forcely by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        return client.user_delete(request, id, force=True)

    @rest_utils.ajax(data_required=True)
    def patch(self, request, id):
        """Update a Container.

        Returns the Container object on success.
        """
        args = client.user_update(request, id, **request.DATA)
        LOG.debug('restapi inside patch User xxxxxx args=%s, xxx' % (args))
        return args

@urls.register
class Providerregion(generic.View):
    """API for retrieving a single container"""
    url_regex = r'zun/providerregions/(?P<id>[^/]+)$'

    @rest_utils.ajax()
    def get(self, request, id):
        LOG.debug('restapi Providerregion xxxxxx get=%s, id=%s xxx' % (request, id))
        """Get a specific container"""
        return change_to_id(client.providerregion_show(request, id).to_dict())

    @rest_utils.ajax(data_required=True)
    def delete(self, request, id):
        """Delete single Container forcely by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        return client.providerregion_delete(request, id, force=True)

    @rest_utils.ajax(data_required=True)
    def patch(self, request, id):
        """Update a Container.

        Returns the Container object on success.
        """
        args = client.providerregion_update(request, id, **request.DATA)
        LOG.debug('restapi inside patch Providerregion xxxxxx args=%s, xxx' % (args))
        return args

@urls.register
class Provider(generic.View):
    """API for retrieving a single container"""
    url_regex = r'zun/providers/(?P<id>[^/]+)$'

    @rest_utils.ajax()
    def get(self, request, id):
        LOG.debug('restapi Provider xxxxxx get=%s, id=%s xxx' % (request, id))
        """Get a specific container"""
        return change_to_id(client.provider_show(request, id).to_dict())

    @rest_utils.ajax(data_required=True)
    def delete(self, request, id):
        """Delete single Container forcely by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        return client.provider_delete(request, id, force=True)

    @rest_utils.ajax(data_required=True)
    def patch(self, request, id):
        """Update a Container.

        Returns the Container object on success.
        """
        args = client.provider_update(request, id, **request.DATA)
        LOG.debug('restapi inside patch Provider xxxxxx args=%s, xxx' % (args))
        return args

@urls.register
class Container(generic.View):
    """API for retrieving a single container"""
    url_regex = r'zun/containers/(?P<id>[^/]+)$'

    @rest_utils.ajax()
    def get(self, request, id):
        """Get a specific container"""
        LOG.debug('restapi Container xxxxxx get=%s, id=%s xxx' % (request, id))
        return change_to_id(client.container_show(request, id).to_dict())

    @rest_utils.ajax(data_required=True)
    def delete(self, request, id):
        """Delete single Container forcely by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        return client.container_delete(request, id, force=True)

    @rest_utils.ajax(data_required=True)
    def patch(self, request, id):
        """Update a Container.

        Returns the Container object on success.
        """
        args = client.container_update(request, id, **request.DATA)
        return args


@urls.register
class ContainerActions(generic.View):
    """API for retrieving a single container"""
    url_regex = r'zun/containers/(?P<id>[^/]+)/(?P<action>[^/]+)$'

    @rest_utils.ajax()
    def get(self, request, id, action):
        """Get a specific container info"""
        if action == 'logs':
            return client.container_logs(request, id)

    @rest_utils.ajax()
    def post(self, request, id, action):
        """Execute a action of the Containers."""
        if action == 'start':
            return client.container_start(request, id)
        elif action == 'stop':
            timeout = request.DATA.get("timeout") or 10
            return client.container_stop(request, id, timeout)
        elif action == 'restart':
            timeout = request.DATA.get("timeout") or 10
            return client.container_restart(request, id, timeout)
        elif action == 'pause':
            return client.container_pause(request, id)
        elif action == 'unpause':
            return client.container_unpause(request, id)
        elif action == 'execute':
            command = request.DATA.get("command")
            return client.container_execute(request, id, command)
        elif action == 'kill':
            signal = request.DATA.get("signal") or None
            return client.container_kill(request, id, signal)
        elif action == 'attach':
            return client.container_attach(request, id)

@urls.register
class Users(generic.View):
    """API for Zun Users"""
    url_regex = r'zun/users/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get a list of the Users for a project.

        The returned result is an object with property 'items' and each
        item under this is a User.
        """
        result = client.user_list(request)
        LOG.debug('restapi Get yyyzzxxxxxx result= %s xxxxxx' % (result))
        return {'items': [change_to_id(n.to_dict()) for n in result]}

    @rest_utils.ajax(data_required=True)
    def delete(self, request):
        """Delete one or more Users by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        for id in request.DATA:
            client.user_delete(request, id)

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Create a new Container.

        Returns the new Container object on success.
        If 'run' attribute is set true, do 'run' instead 'create'
        """
        LOG.debug('users restapi POST xxxxxx %s xxxxx %s xxx' % (request, request.DATA))
        new_container = client.user_create(request, **request.DATA)
        LOG.debug('zunclient post "%s" and url"%s"' % (new_container.uuid, new_container.to_dict()))
        return rest_utils.CreatedResponse(
            '/api/zun/user/%s' % new_container.uuid,
            new_container.to_dict())

@urls.register
class Providerregions(generic.View):
    """API for Zun Containers"""
    url_regex = r'zun/providerregions/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get a list of the Containers for a project.

        The returned result is an object with property 'items' and each
        item under this is a Container.
        """
        result = client.providerregion_list(request)
        LOG.debug('restapi Get yyyzzxxxxxx result= %s xxxxxx' % (result))
        return {'items': [change_to_id(n.to_dict()) for n in result]}

    @rest_utils.ajax(data_required=True)
    def delete(self, request):
        """Delete one or more Containers by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        for id in request.DATA:
            client.providerregion_delete(request, id)

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Create a new Container.

        Returns the new Container object on success.
        If 'run' attribute is set true, do 'run' instead 'create'
        """
        LOG.debug('providerregions restapi POST xxxxxx %s xxxxx %s xxx' % (request, request.DATA))
        new_container = client.providerregion_create(request, **request.DATA)
        LOG.debug('zunclient post "%s" and url"%s"' % (new_container.uuid, new_container.to_dict()))
        return rest_utils.CreatedResponse(
            '/api/zun/providerregion/%s' % new_container.uuid,
            new_container.to_dict())

@urls.register
class Providers(generic.View):
    """API for Zun Containers"""
    url_regex = r'zun/providers/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get a list of the Containers for a project.

        The returned result is an object with property 'items' and each
        item under this is a Container.
        """
        result = client.provider_list(request)
        LOG.debug('restapi Get yyyzzxxxxxx result= %s xxxxxx' % (result))
        return {'items': [change_to_id(n.to_dict()) for n in result]}

    @rest_utils.ajax(data_required=True)
    def delete(self, request):
        """Delete one or more Containers by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        for id in request.DATA:
            client.provider_delete(request, id)

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Create a new Container.

        Returns the new Container object on success.
        If 'run' attribute is set true, do 'run' instead 'create'
        """
        LOG.debug('providers restapi POST xxxxxx %s xxxxx %s xxx' % (request, request.DATA))
        new_container = client.provider_create(request, **request.DATA)
        LOG.debug('zunclient post "%s" and url"%s"' % (new_container.uuid, new_container.to_dict()))
        return rest_utils.CreatedResponse(
            '/api/zun/provider/%s' % new_container.uuid,
            new_container.to_dict())

@urls.register
class Containers(generic.View):
    """API for Zun Containers"""
    url_regex = r'zun/containers/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get a list of the Containers for a project.

        The returned result is an object with property 'items' and each
        item under this is a Container.
        """
        LOG.debug('restapi Get xxxxxx %s xxxxx %s xxx' % (request, request.DATA))
        result = client.container_list(request)
        return {'items': [change_to_id(n.to_dict()) for n in result]}

    @rest_utils.ajax(data_required=True)
    def delete(self, request):
        """Delete one or more Containers by id.

        Returns HTTP 204 (no content) on successful deletion.
        """
        for id in request.DATA:
            client.container_delete(request, id)

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Create a new Container.

        Returns the new Container object on success.
        If 'run' attribute is set true, do 'run' instead 'create'
        """
        LOG.debug('restapi POST xxxxxx %s xxxxx %s xxx' % (request, request.DATA))
        new_container = client.container_create(request, **request.DATA)
        LOG.debug('zunclient post "%s" and url"%s"' % (new_container.uuid, new_container.to_dict()))
        return rest_utils.CreatedResponse(
            '/api/zun/container/%s' % new_container.uuid,
            new_container.to_dict())


@urls.register
class Images(generic.View):
    """API for Zun Images"""
    url_regex = r'zun/images/$'

    @rest_utils.ajax()
    def get(self, request):
        """Get a list of the Images for admin users.

        The returned result is an object with property 'items' and each
        item under this is a Image.
        """
        result = client.image_list(request)
        return {'items': [change_to_id(i.to_dict()) for i in result]}

    @rest_utils.ajax(data_required=True)
    def post(self, request):
        """Create a new Image.

        Returns the new Image object on success.
        """
        new_image = client.image_create(request, **request.DATA)
        return rest_utils.CreatedResponse(
            '/api/zun/image/%s' % new_image.uuid,
            new_image.to_dict())
