# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

import fixtures
from oslo_config import cfg

from zun.common import config

CONF = cfg.CONF
CONF.import_opt('host', 'zun.conf')
CONF.import_opt('connection', 'oslo_db.options', group='database')
CONF.import_opt('sqlite_synchronous', 'oslo_db.options', group='database')


class ConfFixture(fixtures.Fixture):
    """Fixture to manage global conf settings."""

    def _setUp(self):
        CONF.set_default('host', 'fake-mini')
        CONF.set_default('connection', "sqlite://", group='database')
        CONF.set_default('sqlite_synchronous', False, group='database')
        config.parse_args([], default_config_files=[])
        self.addCleanup(CONF.reset)
