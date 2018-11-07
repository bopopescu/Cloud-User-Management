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
   * @ngname horizon.dashboard.container.statements.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.statements.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.statements.create.service',
    'horizon.dashboard.container.statements.update.service',
    'horizon.dashboard.container.statements.delete.service',
    'horizon.dashboard.container.statements.delete-force.service',
    'horizon.dashboard.container.statements.start.service',
    'horizon.dashboard.container.statements.stop.service',
    'horizon.dashboard.container.statements.restart.service',
    'horizon.dashboard.container.statements.pause.service',
    'horizon.dashboard.container.statements.unpause.service',
    'horizon.dashboard.container.statements.execute.service',
    'horizon.dashboard.container.statements.kill.service',
    'horizon.dashboard.container.statements.refresh.service',
    'horizon.dashboard.container.statements.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createStatementService,
    updateStatementService,
    deleteStatementService,
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
    var statementsResourceType = registry.getResourceType(resourceType);

    statementsResourceType.globalActions
      .append({
        id: 'createStatementAction',
        service: createStatementService,
        template: {
          type: 'create',
          text: gettext('Add Statement')
        }
      });

    statementsResourceType.batchActions
      .append({
        id: 'batchDeleteStatementAction',
        service: deleteStatementService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Statements')
        }
      });

    statementsResourceType.itemActions.append({
        id: 'updateStatementAction',
        service: updateStatementService,
        template: {
          text: gettext('Update Statement')
        }
      })
      .append({
        id: 'deleteStatementAction',
        service: deleteStatementService,
        template: {
          type: 'delete',
          text: gettext('Delete Statement')
        }
      });
  }

})();
