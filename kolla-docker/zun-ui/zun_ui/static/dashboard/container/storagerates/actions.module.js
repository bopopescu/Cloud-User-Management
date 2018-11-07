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
   * @ngname horizon.dashboard.container.storagerates.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.storagerates.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.storagerates.create.service',
    'horizon.dashboard.container.storagerates.update.service',
    'horizon.dashboard.container.storagerates.delete.service',
    'horizon.dashboard.container.storagerates.delete-force.service',
    'horizon.dashboard.container.storagerates.start.service',
    'horizon.dashboard.container.storagerates.stop.service',
    'horizon.dashboard.container.storagerates.restart.service',
    'horizon.dashboard.container.storagerates.pause.service',
    'horizon.dashboard.container.storagerates.unpause.service',
    'horizon.dashboard.container.storagerates.execute.service',
    'horizon.dashboard.container.storagerates.kill.service',
    'horizon.dashboard.container.storagerates.refresh.service',
    'horizon.dashboard.container.storagerates.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createStoragerateService,
    updateStoragerateService,
    deleteStoragerateService,
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
    var storageratesResourceType = registry.getResourceType(resourceType);

    storageratesResourceType.globalActions
      .append({
        id: 'createStoragerateAction',
        service: createStoragerateService,
        template: {
          type: 'create',
          text: gettext('Add Storage Rate')
        }
      });

    storageratesResourceType.batchActions
      .append({
        id: 'batchDeleteStoragerateAction',
        service: deleteStoragerateService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Storage Rates')
        }
      });

    storageratesResourceType.itemActions.append({
        id: 'updateStoragerateAction',
        service: updateStoragerateService,
        template: {
          text: gettext('Update Storage Rate')
        }
      })
      .append({
        id: 'deleteStoragerateAction',
        service: deleteStoragerateService,
        template: {
          type: 'delete',
          text: gettext('Delete Storage Rate')
        }
      });
  }

})();
