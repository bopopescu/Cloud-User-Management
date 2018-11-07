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
   * @ngname horizon.dashboard.container.servers.details
   *
   * @description
   * Provides details features for container.
   */
  angular.module('horizon.dashboard.container.servers.details',
                 ['horizon.framework.conf', 'horizon.app.core'])
  .run(registerDetails);

  registerDetails.$inject = [
    'horizon.dashboard.container.servers.basePath',
    'horizon.dashboard.container.servers.resourceType',
    'horizon.dashboard.container.servers.service',
    'horizon.framework.conf.resource-type-registry.service'
  ];

  function registerDetails(
    basePath,
    resourceType,
    containerService,
    registry
  ) {
    registry.getResourceType(resourceType)
      .setLoadFunction(containerService.getContainerPromise)
      .detailsViews
      .append({
        id: 'containerDetailsOverview',
        name: gettext('Overview'),
        template: basePath + 'details/overview.html'
      })
      .append({
        id: 'containerDetailsLogs',
        name: gettext('Logs'),
        template: basePath + 'details/logs.html'
      })
      .append({
        id: 'containerDetailsConsole',
        name: gettext('Console'),
        template: basePath + 'details/console.html'
      });
  }

})();
