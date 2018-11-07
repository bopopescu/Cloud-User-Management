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
   * @ngname horizon.dashboard.container.usages.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.usages.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.usages.create.service',
    'horizon.dashboard.container.usages.update.service',
    'horizon.dashboard.container.usages.delete.service',
    'horizon.dashboard.container.usages.delete-force.service',
    'horizon.dashboard.container.usages.start.service',
    'horizon.dashboard.container.usages.stop.service',
    'horizon.dashboard.container.usages.restart.service',
    'horizon.dashboard.container.usages.pause.service',
    'horizon.dashboard.container.usages.unpause.service',
    'horizon.dashboard.container.usages.execute.service',
    'horizon.dashboard.container.usages.kill.service',
    'horizon.dashboard.container.usages.refresh.service',
    'horizon.dashboard.container.usages.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createUsageService,
    updateUsageService,
    deleteUsageService,
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
    var usagesResourceType = registry.getResourceType(resourceType);

    usagesResourceType.globalActions
      .append({
        id: 'createUsageAction',
        service: createUsageService,
        template: {
          type: 'create',
          text: gettext('Add Usage')
        }
      });

    usagesResourceType.batchActions
      .append({
        id: 'batchDeleteUsageAction',
        service: deleteUsageService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Usages')
        }
      });

    usagesResourceType.itemActions.append({
        id: 'updateUsageAction',
        service: updateUsageService,
        template: {
          text: gettext('Update Usage')
        }
      })
      .append({
        id: 'deleteUsageAction',
        service: deleteUsageService,
        template: {
          type: 'delete',
          text: gettext('Delete Usage')
        }
      });
  }

})();
