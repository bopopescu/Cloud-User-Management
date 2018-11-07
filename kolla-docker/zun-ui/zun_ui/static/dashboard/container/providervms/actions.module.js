/**
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

(function() {
  'use strict';

  /**
   * @ngdoc overview
   * @ngname horizon.dashboard.container.providervms.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.providervms.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.providervms.create.service',
    'horizon.dashboard.container.providervms.update.service',
    'horizon.dashboard.container.providervms.delete.service',
    'horizon.dashboard.container.providervms.delete-force.service',
    'horizon.dashboard.container.providervms.start.service',
    'horizon.dashboard.container.providervms.stop.service',
    'horizon.dashboard.container.providervms.restart.service',
    'horizon.dashboard.container.providervms.pause.service',
    'horizon.dashboard.container.providervms.unpause.service',
    'horizon.dashboard.container.providervms.execute.service',
    'horizon.dashboard.container.providervms.kill.service',
    'horizon.dashboard.container.providervms.refresh.service',
    'horizon.dashboard.container.providervms.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createProvidervmService,
    updateProvidervmService,
    deleteProvidervmService,
    deleteContainerForceService,
    startContainerService,
    stopContainerService,
    restartContainerService,
    pauseContainerService,
    unpauseContainerService,
    executeContainerService,
    killContainerService,
    refreshContainerService,
    resourceType
  ) {
    var providervmsResourceType = registry.getResourceType(resourceType);

    providervmsResourceType.globalActions
      .append({
        id: 'createProvidervmAction',
        service: createProvidervmService,
        template: {
          type: 'create',
          text: gettext('Add Provider VM')
        }
      });

    providervmsResourceType.batchActions
      .append({
        id: 'batchDeleteProvidervmAction',
        service: deleteProvidervmService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Provider VMs')
        }
      });

    providervmsResourceType.itemActions.append({
        id: 'updateProvidervmAction',
        service: updateProvidervmService,
        template: {
          text: gettext('Update Provider VM')
        }
      })
      .append({
        id: 'deleteProvidervmAction',
        service: deleteProvidervmService,
        template: {
          type: 'delete',
          text: gettext('Delete Provider VM')
        }
      });
  }

})();
