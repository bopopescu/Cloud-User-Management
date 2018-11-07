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
   * @ngname horizon.dashboard.container.instances.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.instances.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.instances.create.service',
    'horizon.dashboard.container.instances.update.service',
    'horizon.dashboard.container.instances.delete.service',
    'horizon.dashboard.container.instances.delete-force.service',
    'horizon.dashboard.container.instances.start.service',
    'horizon.dashboard.container.instances.stop.service',
    'horizon.dashboard.container.instances.restart.service',
    'horizon.dashboard.container.instances.pause.service',
    'horizon.dashboard.container.instances.unpause.service',
    'horizon.dashboard.container.instances.execute.service',
    'horizon.dashboard.container.instances.kill.service',
    'horizon.dashboard.container.instances.refresh.service',
    'horizon.dashboard.container.instances.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createInstanceService,
    updateInstanceService,
    deleteInstanceService,
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
    var instancesResourceType = registry.getResourceType(resourceType);

    instancesResourceType.globalActions
      .append({
        id: 'createInstanceAction',
        service: createInstanceService,
        template: {
          type: 'create',
          text: gettext('Add Instance')
        }
      });

    instancesResourceType.batchActions
      .append({
        id: 'batchDeleteInstanceAction',
        service: deleteInstanceService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Instances')
        }
      });

    instancesResourceType.itemActions.append({
        id: 'updateInstanceAction',
        service: updateInstanceService,
        template: {
          text: gettext('Update Instance')
        }
      })
      .append({
        id: 'deleteInstanceAction',
        service: deleteInstanceService,
        template: {
          type: 'delete',
          text: gettext('Delete Instance')
        }
      });
  }

})();
