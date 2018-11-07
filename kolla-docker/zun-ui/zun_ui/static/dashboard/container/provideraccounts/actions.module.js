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
   * @ngname horizon.dashboard.container.provideraccounts.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.provideraccounts.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.provideraccounts.create.service',
    'horizon.dashboard.container.provideraccounts.update.service',
    'horizon.dashboard.container.provideraccounts.delete.service',
    'horizon.dashboard.container.provideraccounts.delete-force.service',
    'horizon.dashboard.container.provideraccounts.start.service',
    'horizon.dashboard.container.provideraccounts.stop.service',
    'horizon.dashboard.container.provideraccounts.restart.service',
    'horizon.dashboard.container.provideraccounts.pause.service',
    'horizon.dashboard.container.provideraccounts.unpause.service',
    'horizon.dashboard.container.provideraccounts.execute.service',
    'horizon.dashboard.container.provideraccounts.kill.service',
    'horizon.dashboard.container.provideraccounts.refresh.service',
    'horizon.dashboard.container.provideraccounts.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createProvideraccountService,
    updateProvideraccountService,
    deleteProvideraccountService,
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
    var provideraccountsResourceType = registry.getResourceType(resourceType);

    provideraccountsResourceType.globalActions
      .append({
        id: 'createProvideraccountAction',
        service: createProvideraccountService,
        template: {
          type: 'create',
          text: gettext('Add Provider Account')
        }
      });

    provideraccountsResourceType.batchActions
      .append({
        id: 'batchDeleteProvideraccountAction',
        service: deleteProvideraccountService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Provider Accounts')
        }
      });

    provideraccountsResourceType.itemActions.append({
        id: 'updateProvideraccountAction',
        service: updateProvideraccountService,
        template: {
          text: gettext('Update Provider Account')
        }
      })
      .append({
        id: 'deleteProvideraccountAction',
        service: deleteProvideraccountService,
        template: {
          type: 'delete',
          text: gettext('Delete Provider Account')
        }
      });
  }

})();
