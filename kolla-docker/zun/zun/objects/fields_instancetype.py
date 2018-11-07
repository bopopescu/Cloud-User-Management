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

import six

from oslo_serialization import jsonutils as json
from oslo_versionedobjects import fields

from zun.common import consts

UnspecifiedDefault = fields.UnspecifiedDefault


class InstancetypeStatus(fields.Enum):
    ALL = consts.CONTAINER_STATUSES

    def __init__(self):
        super(InstancetypeStatus, self).__init__(
            valid_values=InstancetypeStatus.ALL)


class InstancetypeStatusField(fields.BaseEnumField):
    AUTO_TYPE = InstancetypeStatus()