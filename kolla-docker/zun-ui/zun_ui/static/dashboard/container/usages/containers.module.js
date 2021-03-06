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
   * @name horizon.dashboard.container.usages
   * @ngModule
   * @description
   * Provides all the services and widgets require to display the container
   * panel
   */
  angular
    .module('horizon.dashboard.container.usages', [
      'ngRoute',
      'horizon.dashboard.container.usages.actions',
      'horizon.dashboard.container.usages.details'
    ])
    .constant('horizon.dashboard.container.usages.events', events())
    .constant('horizon.dashboard.container.usages.validStates', validStates())
    .constant('horizon.dashboard.container.usages.resourceType', 'OS::Zun::Usage')
    .run(run)
    .config(config);

  /**
   * @ngdoc constant
   * @name horizon.dashboard.container.usages.events
   * @description A list of events used by Container
   * @returns {Object} Event constants
   */
  function events() {
    return {
      CREATE_SUCCESS: 'horizon.dashboard.container.usages.CREATE_SUCCESS',
      DELETE_SUCCESS: 'horizon.dashboard.container.usages.DELETE_SUCCESS'
    };
  }

  function validStates() {
    var states = {
      ERROR: 'Error', RUNNING: 'Running', STOPPED: 'Stopped',
      PAUSED: 'Paused', UNKNOWN: 'Unknown', CREATING: 'Creating',
      CREATED: 'Created', DELETED: 'Deleted'
    };
    return {
      update: [states.CREATED, states.RUNNING, states.STOPPED, states.PAUSED],
      start: [states.CREATED, states.STOPPED, states.ERROR],
      stop: [states.RUNNING],
      restart: [states.CREATED, states.RUNNING, states.STOPPED, states.ERROR],
      pause: [states.RUNNING],
      unpause: [states.PAUSED],
      execute: [states.RUNNING],
      kill: [states.RUNNING],
      delete: [states.CREATED, states.ERROR, states.STOPPED, states.DELETED],
      delete_force: [
        states.CREATED, states.CREATING, states.ERROR, states.RUNNING,
        states.STOPPED, states.UNKNOWN, states.DELETED
      ]
    };
  }

  run.$inject = [
    'horizon.framework.conf.resource-type-registry.service',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.usages.basePath',
    'horizon.dashboard.container.usages.resourceType',
    'horizon.dashboard.container.usages.service'
  ];

  function run(registry, zun, basePath, resourceType, containerService) {
    registry.getResourceType(resourceType)
    .setNames(gettext('Account'), gettext('Usages'))
    // for detail summary view on table row.
    .setSummaryTemplateUrl(basePath + 'details/drawer.html')
    // for table row items and detail summary view.
    .setProperties(containerProperties())
    .setListFunction(containerService.getContainersPromise)
    .tableColumns
    .append({
      id: 'displayname',
      priority: 1,
      sortDefault: true,
      filters: ['noName'],
      urlFunction: containerService.getDetailsPath
    })
    .append({
      id: 'displayname2',
      priority: 2
    })
    .append({
      id: 'displayname3',
      priority: 2
    })
    .append({
      id: 'displayname4',
      priority: 2
    });
    // for magic-search
    registry.getResourceType(resourceType).filterFacets
    .append({
      'label': gettext('Usage ID'),
      'name': 'id',
      'singleton': true
    })
    .append({
      'label': gettext('User ID'),
      'name': 'user_id',
      'singleton': true
    });
  }

  function containerProperties() {
    return {
      'id': {label: gettext('Usage ID'), filters: ['noValue'] },
      'user_id': {label: gettext('User ID'), filters: ['noValue'] },
      'instance_id': {label: gettext('Instance ID'), filters: ['noValue'] },
      'compute_rate_id': {label: gettext('Compute Rate ID'), filters: ['noValue'] },
      'storage_rate_id': {label: gettext('Storage Rate ID'), filters: ['noValue'] },
      'start_time': {label: gettext('Start Time'), filters: ['noValue'] },
      'stop_time': {label: gettext('Stop Time'), filters: ['noValue'] },
      'duration': {label: gettext('Duration'), filters: ['noValue'] },
      'cost': {label: gettext('Cost'), filters: ['noValue'] },
      'displayname': {label: gettext('Displayname'), filters: ['noValue'] },
      'displayname2': {label: gettext('Displayname2'), filters: ['noValue'] },
      'displayname3': {label: gettext('Displayname3'), filters: ['noValue'] },
      'displayname4': {label: gettext('Displayname4'), filters: ['noValue'] },
    };
  }

  config.$inject = [
    '$provide',
    '$windowProvider',
    '$routeProvider'
  ];

  /**
   * @name config
   * @param {Object} $provide
   * @param {Object} $windowProvider
   * @param {Object} $routeProvider
   * @description Routes used by this module.
   * @returns {undefined} Returns nothing
   */
  function config($provide, $windowProvider, $routeProvider) {
    var path = $windowProvider.$get().STATIC_URL + 'dashboard/container/usages/';
    $provide.constant('horizon.dashboard.container.usages.basePath', path);
    $routeProvider.when('/admin/container/usages', {
      templateUrl: path + 'panel.html'
    });
  }
})();
