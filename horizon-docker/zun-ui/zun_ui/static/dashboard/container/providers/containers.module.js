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
   * @name horizon.dashboard.container.providers
   * @ngModule
   * @description
   * Provides all the services and widgets require to display the container
   * panel
   */
  angular
    .module('horizon.dashboard.container.providers', [
      'ngRoute',
      'horizon.dashboard.container.providers.actions',
      'horizon.dashboard.container.providers.details'
    ])
    .constant('horizon.dashboard.container.providers.events', events())
    .constant('horizon.dashboard.container.providers.validStates', validStates())
    .constant('horizon.dashboard.container.providers.resourceType', 'OS::Zun::Provider')
    .run(run)
    .config(config);

  /**
   * @ngdoc constant
   * @name horizon.dashboard.container.providers.events
   * @description A list of events used by Container
   * @returns {Object} Event constants
   */
  function events() {
    return {
      CREATE_SUCCESS: 'horizon.dashboard.container.providers.CREATE_SUCCESS',
      DELETE_SUCCESS: 'horizon.dashboard.container.providers.DELETE_SUCCESS'
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
    'horizon.dashboard.container.providers.basePath',
    'horizon.dashboard.container.providers.resourceType',
    'horizon.dashboard.container.providers.service'
  ];

  function run(registry, zun, basePath, resourceType, containerService) {
    registry.getResourceType(resourceType)
    .setNames(gettext('Account'), gettext('Accounts'))
    // for detail summary view on table row.
    .setSummaryTemplateUrl(basePath + 'details/drawer.html')
    // for table row items and detail summary view.
    .setProperties(containerProperties())
    .setListFunction(containerService.getContainersPromise)
    .tableColumns
    .append({
      id: 'id',
      priority: 1,
      sortDefault: true,
      filters: ['noName'],
      urlFunction: containerService.getDetailsPath
    })
    .append({
      id: 'provider',
      priority: 2
    });
    // for magic-search
    registry.getResourceType(resourceType).filterFacets
    .append({
      'label': gettext('Provider ID'),
      'name': 'id',
      'singleton': true
    })
    .append({
      'label': gettext('Provider'),
      'name': 'provider',
      'singleton': true
    });
  }

  function containerProperties() {
    return {
      'id': {label: gettext('Provider ID'), filters: ['noValue'] },
      'provider': {label: gettext('Provider'), filters: ['noValue'] },
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
    var path = $windowProvider.$get().STATIC_URL + 'dashboard/container/providers/';
    $provide.constant('horizon.dashboard.container.providers.basePath', path);
    $routeProvider.when('/admin/container/providers', {
      templateUrl: path + 'panel.html'
    });
  }
})();
