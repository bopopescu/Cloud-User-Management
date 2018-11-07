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
   * @ngname horizon.dashboard.container.servers.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.servers.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.servers.create.service',
    'horizon.dashboard.container.servers.update.service',
    'horizon.dashboard.container.servers.delete.service',
    'horizon.dashboard.container.servers.delete-force.service',
    'horizon.dashboard.container.servers.start.service',
    'horizon.dashboard.container.servers.stop.service',
    'horizon.dashboard.container.servers.restart.service',
    'horizon.dashboard.container.servers.pause.service',
    'horizon.dashboard.container.servers.unpause.service',
    'horizon.dashboard.container.servers.execute.service',
    'horizon.dashboard.container.servers.kill.service',
    'horizon.dashboard.container.servers.refresh.service',
    'horizon.dashboard.container.servers.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createContainerService,
    updateContainerService,
    deleteContainerService,
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
    var containersResourceType = registry.getResourceType(resourceType);

    containersResourceType.globalActions
      .append({
        id: 'createContainerAction',
        service: createContainerService,
        template: {
          type: 'create',
          text: gettext('Create Serverxxx')
        }
      })
     .append({
        id: 'createContainerAction',
        service: createContainerService,
        template: {
          type: 'create',
          text: gettext('Create Serverxxx2')
        }
      });

    containersResourceType.batchActions
      .append({
        id: 'batchDeleteContainerAction',
        service: deleteContainerService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Containers')
        }
      });

    containersResourceType.itemActions
      .append({
        id: 'refreshContainerAction',
        service: refreshContainerService,
        template: {
          text: gettext('Refresh')
        }
      })
      .append({
        id: 'updateContainerAction',
        service: updateContainerService,
        template: {
          text: gettext('Update Container')
        }
      })
      .append({
        id: 'startContainerAction',
        service: startContainerService,
        template: {
          text: gettext('Start Container')
        }
      })
      .append({
        id: 'stopContainerAction',
        service: stopContainerService,
        template: {
          text: gettext('Stop Container')
        }
      })
      .append({
        id: 'restartContainerAction',
        service: restartContainerService,
        template: {
          text: gettext('Restart Container')
        }
      })
      .append({
        id: 'pauseContainerAction',
        service: pauseContainerService,
        template: {
          text: gettext('Pause Container')
        }
      })
      .append({
        id: 'unpauseContainerAction',
        service: unpauseContainerService,
        template: {
          text: gettext('Unpause Container')
        }
      })
      .append({
        id: 'executeContainerAction',
        service: executeContainerService,
        template: {
          text: gettext('Execute Command')
        }
      })
      .append({
        id: 'killContainerAction',
        service: killContainerService,
        template: {
          text: gettext('Send Kill Signal')
        }
      })
      .append({
        id: 'deleteContainerAction',
        service: deleteContainerService,
        template: {
          type: 'delete',
          text: gettext('Delete Container')
        }
      })
      .append({
        id: 'deleteContainerForceAction',
        service: deleteContainerForceService,
        template: {
          type: 'delete',
          text: gettext('Delete Container Forcely')
        }
      });
  }

})();
