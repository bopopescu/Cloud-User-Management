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
   * @ngname horizon.dashboard.container.instancetypes.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.instancetypes.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.instancetypes.create.service',
    'horizon.dashboard.container.instancetypes.update.service',
    'horizon.dashboard.container.instancetypes.delete.service',
    'horizon.dashboard.container.instancetypes.delete-force.service',
    'horizon.dashboard.container.instancetypes.start.service',
    'horizon.dashboard.container.instancetypes.stop.service',
    'horizon.dashboard.container.instancetypes.restart.service',
    'horizon.dashboard.container.instancetypes.pause.service',
    'horizon.dashboard.container.instancetypes.unpause.service',
    'horizon.dashboard.container.instancetypes.execute.service',
    'horizon.dashboard.container.instancetypes.kill.service',
    'horizon.dashboard.container.instancetypes.refresh.service',
    'horizon.dashboard.container.instancetypes.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createInstancetypeService,
    updateInstancetypeService,
    deleteInstancetypeService,
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
    var instancetypesResourceType = registry.getResourceType(resourceType);

    instancetypesResourceType.globalActions
      .append({
        id: 'createInstancetypeAction',
        service: createInstancetypeService,
        template: {
          type: 'create',
          text: gettext('Add Instance Type')
        }
      });

    instancetypesResourceType.batchActions
      .append({
        id: 'batchDeleteInstancetypeAction',
        service: deleteInstancetypeService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Instance Types')
        }
      });

    instancetypesResourceType.itemActions.append({
        id: 'updateInstancetypeAction',
        service: updateInstancetypeService,
        template: {
          text: gettext('Update Instance Type')
        }
      })
      .append({
        id: 'deleteInstancetypeAction',
        service: deleteInstancetypeService,
        template: {
          type: 'delete',
          text: gettext('Delete Instance Type')
        }
      });
  }

})();
