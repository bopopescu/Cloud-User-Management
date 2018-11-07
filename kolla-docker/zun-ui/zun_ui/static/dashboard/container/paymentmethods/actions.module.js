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
   * @ngname horizon.dashboard.container.paymentmethods.actions
   *
   * @description
   * Provides all of the actions for containers.
   */
  angular.module('horizon.dashboard.container.paymentmethods.actions',
    [
      'horizon.framework',
      'horizon.dashboard.container'
    ])
    .run(registerContainerActions);

  registerContainerActions.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.dashboard.container.paymentmethods.create.service',
    'horizon.dashboard.container.paymentmethods.update.service',
    'horizon.dashboard.container.paymentmethods.delete.service',
    'horizon.dashboard.container.paymentmethods.delete-force.service',
    'horizon.dashboard.container.paymentmethods.start.service',
    'horizon.dashboard.container.paymentmethods.stop.service',
    'horizon.dashboard.container.paymentmethods.restart.service',
    'horizon.dashboard.container.paymentmethods.pause.service',
    'horizon.dashboard.container.paymentmethods.unpause.service',
    'horizon.dashboard.container.paymentmethods.execute.service',
    'horizon.dashboard.container.paymentmethods.kill.service',
    'horizon.dashboard.container.paymentmethods.refresh.service',
    'horizon.dashboard.container.paymentmethods.resourceType'
  ];

  function registerContainerActions(
    registry,
    gettext,
    createPaymentmethodService,
    updatePaymentmethodService,
    deletePaymentmethodService,
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
    var paymentmethodsResourceType = registry.getResourceType(resourceType);

    paymentmethodsResourceType.globalActions
      .append({
        id: 'createPaymentmethodAction',
        service: createPaymentmethodService,
        template: {
          type: 'create',
          text: gettext('Add Payment Method')
        }
      });

    paymentmethodsResourceType.batchActions
      .append({
        id: 'batchDeletePaymentmethodAction',
        service: deletePaymentmethodService,
        template: {
          type: 'delete-selected',
          text: gettext('Delete Payment Methods')
        }
      });

    paymentmethodsResourceType.itemActions.append({
        id: 'updatePaymentmethodAction',
        service: updatePaymentmethodService,
        template: {
          text: gettext('Update Payment Method')
        }
      })
      .append({
        id: 'deletePaymentmethodAction',
        service: deletePaymentmethodService,
        template: {
          type: 'delete',
          text: gettext('Delete Payment Method')
        }
      });
  }

})();
