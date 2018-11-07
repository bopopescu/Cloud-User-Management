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
   * @ngname horizon.dashboard.container.providerregions.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.providerregions.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.providerregions.create.service',
    'horizon.dashboard.container.providerregions.update.service',
    'horizon.dashboard.container.providerregions.delete.service',
    'horizon.dashboard.container.providerregions.delete-force.service',
    'horizon.dashboard.container.providerregions.start.service',
    'horizon.dashboard.container.providerregions.stop.service',
    'horizon.dashboard.container.providerregions.restart.service',
    'horizon.dashboard.container.providerregions.pause.service',
    'horizon.dashboard.container.providerregions.unpause.service',
    'horizon.dashboard.container.providerregions.execute.service',
    'horizon.dashboard.container.providerregions.kill.service',
    'horizon.dashboard.container.providerregions.refresh.service',
    'horizon.dashboard.container.providerregions.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createProviderregionService,
    updateProviderregionService,
    deleteProviderregionService,
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
    var providerregionsResourceType = registry.getResourceType(resourceType);

    providerregionsResourceType.globalActions
      .append({
        id: 'createProviderregionAction',
        service: createProviderregionService,
        template: {
          type: 'create',
          text: gettext('Add Account')
        }
      });

    providerregionsResourceType.batchActions
      .append({
        id: 'batchDeleteProviderregionAction',
        service: deleteProviderregionService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Accounts')
        }
      });

    providerregionsResourceType.itemActions.append({
        id: 'updateProviderregionAction',
        service: updateProviderregionService,
        template: {
          text: gettext('Update Account')
        }
      })
      .append({
        id: 'deleteProviderregionAction',
        service: deleteProviderregionService,
        template: {
          type: 'delete',
          text: gettext('Delete Account')
        }
      });
  }

})();
