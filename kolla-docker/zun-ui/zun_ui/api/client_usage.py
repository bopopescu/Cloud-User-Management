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

from horizon import exceptions
from horizon.utils.memoized import memoized_with_request
import logging
from openstack_dashboard.api import base
from zunclient.common import utils
from zunclient.v1 import client as zun_client


LOG = logging.getLogger(__name__)


USAGE_CREATE_ATTRS = zun_client.usages.CREATION_ATTRIBUTES
CONTAINER_CREATE_ATTRS = zun_client.containers.CREATION_ATTRIBUTES
SERVER_CREATE_ATTRS = zun_client.containers.CREATION_ATTRIBUTES

IMAGE_PULL_ATTRS = zun_client.images.PULL_ATTRIBUTES


def get_auth_params_from_request(request):
    """Extracts properties needed by zunclient call from the request object.

    These will be used to memoize the calls to zunclient.
    """
    endpoint_override = ""
    try:
        endpoint_override = base.url_for(request, 'container')
    except exceptions.ServiceCatalogException:
        LOG.debug('No Container Management service is configured.')
        return None
    return (
        request.user.username,
        request.user.token.id,
        request.user.tenant_id,
        endpoint_override
    )


@memoized_with_request(get_auth_params_from_request)
def zunclient(request_auth_params):
    (
        username,
        token_id,
        project_id,
        endpoint_override
    ) = request_auth_params

    LOG.debug('zunclient connection created using the token "%s" and url'
              ' "%s"' % (token_id, endpoint_override))
    c = zun_client.Client(username=username,
                          project_id=project_id,
                          auth_token=token_id,
                          endpoint_override=endpoint_override)
    return c




def _cleanup_usage_params(attrs, check, **params):
    args = {}
    run = False

    for (key, value) in params.items():
        if key == "run":
            run = value
        elif key == "cpu":
            args[key] = float(value)
        elif key == "memory":
            args[key] = int(value)
        elif key == "interactive" or key == "nets" \
                or key == "security_groups" or key == "hints":
            args[key] = value
        elif key == "restart_policy":
            args[key] = utils.check_restart_policy(value)
        elif key == "environment" or key == "labels":
            values = {}
            vals = value.split(",")
            for v in vals:
                kv = v.split("=", 1)
                values[kv[0]] = kv[1]
            args[str(key)] = values
        elif key in attrs:
            if value is None:
                value = ''
            args[str(key)] = str(value)
        elif check:
            LOG.debug('zunclient xxx exception %s xxx' % key)
            raise exceptions.BadRequest(
                "Key must be in %s" % ",".join(attrs))

    return args, run

def _cleanup_params(attrs, check, **params):
    args = {}
    run = False

    for (key, value) in params.items():
        if key == "run":
            run = value
        elif key == "cpu":
            args[key] = float(value)
        elif key == "memory":
            args[key] = int(value)
        elif key == "interactive" or key == "nets" \
                or key == "security_groups" or key == "hints":
            args[key] = value
        elif key == "restart_policy":
            args[key] = utils.check_restart_policy(value)
        elif key == "environment" or key == "labels":
            values = {}
            vals = value.split(",")
            for v in vals:
                kv = v.split("=", 1)
                values[kv[0]] = kv[1]
            args[str(key)] = values
        elif key in attrs:
            if value is None:
                value = ''
            args[str(key)] = str(value)
        elif check:
            LOG.debug('zunclient xxx exception %s xxx' % key)
            raise exceptions.BadRequest(
                "Key must be in %s" % ",".join(attrs))

    return args, run


def _delete_attributes_with_same_value(old, new):
    '''Delete attributes with same value from new dict

    If new dict has same value in old dict, remove the attributes
    from new dict.
    '''
    for k in old.keys():
        if k in new:
            if old[k] == new[k]:
                del new[k]
    return new



def usage_create(request, **kwargs):
    LOG.debug('xxx start usage_create xxx %s' % kwargs)
    args, run = _cleanup_params(USAGE_CREATE_ATTRS, True, **kwargs)
    response = None
    response = zunclient(request).usages.create(**args)
    return response

def container_create(request, **kwargs):
    LOG.debug('xxx start container_create xxx %s' % kwargs)
    args, run = _cleanup_params(CONTAINER_CREATE_ATTRS, True, **kwargs)
    response = None
    response = zunclient(request).containers.create(**args)
    #if run:
    #    response = zunclient(request).containers.run(**args)
    #else:
    #    response = zunclient(request).containers.create(**args)
    return response



def usage_update(request, id, **kwargs):
    '''Update Container

    Get current Usage attributes and check updates.
    And update with "rename" for "name", then use "update" for
    "cpu" and "memory".
    '''

    # get current data
    container = zunclient(request).usages.get(id).to_dict()
    account_name = container["id"]
    args, run = _cleanup_usage_params(USAGE_CREATE_ATTRS, True, **kwargs)
    # remove same values from new params
    _delete_attributes_with_same_value(container, args)
    # do rename
    name = args.pop("id", None)
    #LOG.debug('xxxx zun-ui client usage_update name=%s, args=%s, len=%s, tmp_account=%s', name, args, len(args),tmp_account)
    if len(args):
        zunclient(request).usages.update(id, **args)

    # do update
    if name:
        zunclient(request).usages.rename(id, name)
        args["id"] = name

    args["id"] = account_name
    return args

def container_update(request, id, **kwargs):
    '''Update Container

    Get current Container attributes and check updates.
    And update with "rename" for "name", then use "update" for
    "cpu" and "memory".
    '''

    # get current data
    container = zunclient(request).containers.get(id).to_dict()
    if container["memory"] is not None:
        container["memory"] = int(container["memory"].replace("M", ""))
    args, run = _cleanup_params(CONTAINER_CREATE_ATTRS, True, **kwargs)

    # remove same values from new params
    _delete_attributes_with_same_value(container, args)

    # do rename
    name = args.pop("name", None)
    if len(args):
        zunclient(request).containers.update(id, **args)

    # do update
    if name:
        zunclient(request).containers.rename(id, name)
        args["name"] = name
    return args



def usage_delete(request, id, force=False):
    # TODO(shu-mutou): force option should be provided by user.
    return zunclient(request).usages.delete(id, force=force)

def container_delete(request, id, force=False):
    # TODO(shu-mutou): force option should be provided by user.
    return zunclient(request).containers.delete(id, force=force)



def usage_list(request, limit=None, marker=None, sort_key=None,
                   sort_dir=None, detail=True):
    # TODO(shu-mutou): detail option should be added, if it is
    # implemented in Zun API
    return zunclient(request).usages.list(limit, marker, sort_key,
                                              sort_dir)

def container_list(request, limit=None, marker=None, sort_key=None,
                   sort_dir=None, detail=True):
    # TODO(shu-mutou): detail option should be added, if it is
    # implemented in Zun API
    return zunclient(request).containers.list(limit, marker, sort_key,
                                              sort_dir)



def usage_show(request, id):
    return zunclient(request).usages.get(id)

def container_show(request, id):
    return zunclient(request).containers.get(id)


def container_logs(request, id):
    args = {}
    args["stdout"] = True
    args["stderr"] = True
    return zunclient(request).containers.logs(id, **args)


def container_start(request, id):
    return zunclient(request).containers.start(id)


def container_stop(request, id, timeout):
    return zunclient(request).containers.stop(id, timeout)


def container_restart(request, id, timeout):
    return zunclient(request).containers.restart(id, timeout)


def container_pause(request, id):
    return zunclient(request).containers.pause(id)


def container_unpause(request, id):
    return zunclient(request).containers.unpause(id)


def container_execute(request, id, command):
    args = {"command": command}
    return zunclient(request).containers.execute(id, **args)


def container_kill(request, id, signal=None):
    return zunclient(request).containers.kill(id, signal)


def container_attach(request, id):
    return zunclient(request).containers.attach(id)



def image_list(request, limit=None, marker=None, sort_key=None,
               sort_dir=None, detail=True):
    return zunclient(request).images.list(limit, marker, sort_key,
                                          sort_dir, False)


def image_create(request, **kwargs):
    args, run = _cleanup_params(IMAGE_PULL_ATTRS, True, **kwargs)
    return zunclient(request).images.create(**args)
