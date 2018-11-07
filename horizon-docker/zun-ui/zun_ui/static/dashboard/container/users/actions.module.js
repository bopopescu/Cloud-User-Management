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
   * @ngname horizon.dashboard.container.users.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.users.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.users.create.service',
    'horizon.dashboard.container.users.update.service',
    'horizon.dashboard.container.users.delete.service',
    'horizon.dashboard.container.users.delete-force.service',
    'horizon.dashboard.container.users.start.service',
    'horizon.dashboard.container.users.stop.service',
    'horizon.dashboard.container.users.restart.service',
    'horizon.dashboard.container.users.pause.service',
    'horizon.dashboard.container.users.unpause.service',
    'horizon.dashboard.container.users.execute.service',
    'horizon.dashboard.container.users.kill.service',
    'horizon.dashboard.container.users.refresh.service',
    'horizon.dashboard.container.users.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createUserService,
    updateUserService,
    deleteUserService,
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
    var usersResourceType = registry.getResourceType(resourceType);

    usersResourceType.globalActions
      .append({
        id: 'createUserAction',
        service: createUserService,
        template: {
          type: 'create',
          text: gettext('Add Account3')
        }
      });

    usersResourceType.batchActions
      .append({
        id: 'batchDeleteUserAction',
        service: deleteUserService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Accounts')
        }
      });

    usersResourceType.itemActions.append({
        id: 'updateUserAction',
        service: updateUserService,
        template: {
          text: gettext('Update Account')
        }
      })
      .append({
        id: 'deleteUserAction',
        service: deleteUserService,
        template: {
          type: 'delete',
          text: gettext('Delete Account')
        }
      });
  }

})();
