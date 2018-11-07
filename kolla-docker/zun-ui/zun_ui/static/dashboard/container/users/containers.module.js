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
   * @name horizon.dashboard.container.users
   * @ngModule
   * @description
   * Provides all the services and widgets require to display the container
   * panel
   */
  angular
    .module('horizon.dashboard.container.users', [
      'ngRoute',
      'horizon.dashboard.container.users.actions',
      'horizon.dashboard.container.users.details'
    ])
    .constant('horizon.dashboard.container.users.events', events())
    .constant('horizon.dashboard.container.users.validStates', validStates())
    .constant('horizon.dashboard.container.users.resourceType', 'OS::Zun::User')
    .run(run)
    .config(config);

  /**
   * @ngdoc constant
   * @name horizon.dashboard.container.users.events
   * @description A list of events used by Container
   * @returns {Object} Event constants
   */
  function events() {
    return {
      CREATE_SUCCESS: 'horizon.dashboard.container.users.CREATE_SUCCESS',
      DELETE_SUCCESS: 'horizon.dashboard.container.users.DELETE_SUCCESS'
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
    'horizon.dashboard.container.users.basePath',
    'horizon.dashboard.container.users.resourceType',
    'horizon.dashboard.container.users.service'
  ];

  function run(registry, zun, basePath, resourceType, containerService) {
    registry.getResourceType(resourceType)
    .setNames(gettext('Account'), gettext('Users'))
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
    });
    // for magic-search
    registry.getResourceType(resourceType).filterFacets
    .append({
      'label': gettext('User ID'),
      'name': 'id',
      'singleton': true
    })
    .append({
      'label': gettext('User Name'),
      'name': 'user_name',
      'singleton': true
    });
  }

  function containerProperties() {
    return {
      'id': {label: gettext('User ID'), filters: ['noValue'] },
      'user_name': {label: gettext('User Name'), filters: ['noValue'] },
      'last_name': {label: gettext('Last Name'), filters: ['noValue'] },
      'first_name': {label: gettext('First Name'), filters: ['noValue'] },
      'middle_name': {label: gettext('Middle Name'), filters: ['noValue'] },
      'password': {label: gettext('Password'), filters: ['noValue'] },
      'account_status': {label: gettext('Account Status'), filters: ['noValue'] },
      'failed_attempt': {label: gettext('Failed Attempt'), filters: ['noValue'] },
      'last_login_method': {label: gettext('Last Login Method'), filters: ['noValue'] },
      'current_user_charge_tier': {label: gettext('Current User Charge Tier'), filters: ['noValue'] },
      'admin_ind': {label: gettext('Admin IND'), filters: ['noValue'] },
      'displayname': {label: gettext('Displayname'), filters: ['noValue'] },
      'passreset_url': {label: gettext('Passoword Reset URL'), filters: ['noValue'] },
      'activation_url': {label: gettext('Activation URL'), filters: ['noValue'] },
      'activation_expir_date': {label: gettext('Activation Expiration Date'), filters: ['noValue'] },
      'passreset_expir_date': {label: gettext('Password Reset Expiration Date'), filters: ['noValue'] },
      'last_login_time': {label: gettext('Last Login Time'), filters: ['noValue'] },
      'last_success_login_ip': {label: gettext('Last Success Login IP'), filters: ['noValue'] },
      'last_failed_login_ip': {label: gettext('Last Failed Login IP'), filters: ['noValue'] },


      /*'user_name': {label: gettext('User'), filters: ['noValue'] },
      'user_access_key_id': {label: gettext('Access Key ID'), filters: ['noValue'] },
      'user_access_key': {label: gettext('Access Key'), filters: ['noValue'] },
      'links': {label: gettext('Links'), filters: ['noValue', 'json'] },
      'name': {label: gettext('Account'), filters: ['noName'] },
      'restart_policy': {label: gettext('Restart Policy'), filters: ['noValue', 'json'] },
      'status': {label: gettext('Status'), filters: ['noValue'] },
      'status_detail': {label: gettext('Status Detail'), filters: ['noValue'] },
      'status_reason': {label: gettext('Status Reason'), filters: ['noValue'] },
      'task_state': {label: gettext('Task State'), filters: ['noValue'] }*/
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
    var path = $windowProvider.$get().STATIC_URL + 'dashboard/container/users/';
    $provide.constant('horizon.dashboard.container.users.basePath', path);
    $routeProvider.when('/admin/container/users', {
      templateUrl: path + 'panel.html'
    });
  }
})();
