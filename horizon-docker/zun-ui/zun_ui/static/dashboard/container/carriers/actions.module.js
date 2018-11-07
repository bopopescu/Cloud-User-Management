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
   * @ngname horizon.dashboard.container.carriers.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.carriers.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.carriers.create.service',
    'horizon.dashboard.container.carriers.update.service',
    'horizon.dashboard.container.carriers.delete.service',
    'horizon.dashboard.container.carriers.delete-force.service',
    'horizon.dashboard.container.carriers.start.service',
    'horizon.dashboard.container.carriers.stop.service',
    'horizon.dashboard.container.carriers.restart.service',
    'horizon.dashboard.container.carriers.pause.service',
    'horizon.dashboard.container.carriers.unpause.service',
    'horizon.dashboard.container.carriers.execute.service',
    'horizon.dashboard.container.carriers.kill.service',
    'horizon.dashboard.container.carriers.refresh.service',
    'horizon.dashboard.container.carriers.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createCarrierService,
    updateCarrierService,
    deleteCarrierService,
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
    var carriersResourceType = registry.getResourceType(resourceType);

    carriersResourceType.globalActions
      .append({
        id: 'createCarrierAction',
        service: createCarrierService,
        template: {
          type: 'create',
          text: gettext('Add Account')
        }
      });

    carriersResourceType.batchActions
      .append({
        id: 'batchDeleteCarrierAction',
        service: deleteCarrierService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Accounts')
        }
      });

    carriersResourceType.itemActions.append({
        id: 'updateCarrierAction',
        service: updateCarrierService,
        template: {
          text: gettext('Update Account')
        }
      })
      .append({
        id: 'deleteCarrierAction',
        service: deleteCarrierService,
        template: {
          type: 'delete',
          text: gettext('Delete Account')
        }
      });
  }

})();
