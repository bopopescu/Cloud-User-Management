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
   * @ngname horizon.dashboard.container.payments.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.payments.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.payments.create.service',
    'horizon.dashboard.container.payments.update.service',
    'horizon.dashboard.container.payments.delete.service',
    'horizon.dashboard.container.payments.delete-force.service',
    'horizon.dashboard.container.payments.start.service',
    'horizon.dashboard.container.payments.stop.service',
    'horizon.dashboard.container.payments.restart.service',
    'horizon.dashboard.container.payments.pause.service',
    'horizon.dashboard.container.payments.unpause.service',
    'horizon.dashboard.container.payments.execute.service',
    'horizon.dashboard.container.payments.kill.service',
    'horizon.dashboard.container.payments.refresh.service',
    'horizon.dashboard.container.payments.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createPaymentService,
    updatePaymentService,
    deletePaymentService,
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
    var paymentsResourceType = registry.getResourceType(resourceType);

    paymentsResourceType.globalActions
      .append({
        id: 'createPaymentAction',
        service: createPaymentService,
        template: {
          type: 'create',
          text: gettext('Add Payment')
        }
      });

    paymentsResourceType.batchActions
      .append({
        id: 'batchDeletePaymentAction',
        service: deletePaymentService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Payments')
        }
      });

    paymentsResourceType.itemActions.append({
        id: 'updatePaymentAction',
        service: updatePaymentService,
        template: {
          text: gettext('Update Payment')
        }
      })
      .append({
        id: 'deletePaymentAction',
        service: deletePaymentService,
        template: {
          type: 'delete',
          text: gettext('Delete Payment')
        }
      });
  }

})();
