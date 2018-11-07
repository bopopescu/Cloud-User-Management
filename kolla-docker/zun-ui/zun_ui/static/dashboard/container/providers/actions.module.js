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
   * @ngname horizon.dashboard.container.providers.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.providers.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.providers.create.service',
    'horizon.dashboard.container.providers.update.service',
    'horizon.dashboard.container.providers.delete.service',
    'horizon.dashboard.container.providers.delete-force.service',
    'horizon.dashboard.container.providers.start.service',
    'horizon.dashboard.container.providers.stop.service',
    'horizon.dashboard.container.providers.restart.service',
    'horizon.dashboard.container.providers.pause.service',
    'horizon.dashboard.container.providers.unpause.service',
    'horizon.dashboard.container.providers.execute.service',
    'horizon.dashboard.container.providers.kill.service',
    'horizon.dashboard.container.providers.refresh.service',
    'horizon.dashboard.container.providers.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createProviderService,
    updateProviderService,
    deleteProviderService,
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
    var providersResourceType = registry.getResourceType(resourceType);

    providersResourceType.globalActions
      .append({
        id: 'createProviderAction',
        service: createProviderService,
        template: {
          type: 'create',
          text: gettext('Add Provider')
        }
      });

    providersResourceType.batchActions
      .append({
        id: 'batchDeleteProviderAction',
        service: deleteProviderService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Providers')
        }
      });

    providersResourceType.itemActions.append({
        id: 'updateProviderAction',
        service: updateProviderService,
        template: {
          text: gettext('Update Provider')
        }
      })
      .append({
        id: 'deleteProviderAction',
        service: deleteProviderService,
        template: {
          type: 'delete',
          text: gettext('Delete Provider')
        }
      });
  }

})();
