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
   * @ngname horizon.dashboard.container.computerates.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.computerates.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.computerates.create.service',
    'horizon.dashboard.container.computerates.update.service',
    'horizon.dashboard.container.computerates.delete.service',
    'horizon.dashboard.container.computerates.delete-force.service',
    'horizon.dashboard.container.computerates.start.service',
    'horizon.dashboard.container.computerates.stop.service',
    'horizon.dashboard.container.computerates.restart.service',
    'horizon.dashboard.container.computerates.pause.service',
    'horizon.dashboard.container.computerates.unpause.service',
    'horizon.dashboard.container.computerates.execute.service',
    'horizon.dashboard.container.computerates.kill.service',
    'horizon.dashboard.container.computerates.refresh.service',
    'horizon.dashboard.container.computerates.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createComputerateService,
    updateComputerateService,
    deleteComputerateService,
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
    var computeratesResourceType = registry.getResourceType(resourceType);

    computeratesResourceType.globalActions
      .append({
        id: 'createComputerateAction',
        service: createComputerateService,
        template: {
          type: 'create',
          text: gettext('Add Compute Rate')
        }
      });

    computeratesResourceType.batchActions
      .append({
        id: 'batchDeleteComputerateAction',
        service: deleteComputerateService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Compute Rates')
        }
      });

    computeratesResourceType.itemActions.append({
        id: 'updateComputerateAction',
        service: updateComputerateService,
        template: {
          text: gettext('Update Compute Rate')
        }
      })
      .append({
        id: 'deleteComputerateAction',
        service: deleteComputerateService,
        template: {
          type: 'delete',
          text: gettext('Delete Compute Rate')
        }
      });
  }

})();
