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
   * @name horizon.dashboard.container.paymentmethods
   * @ngModule
   * @description
   * Provides all the services and widgets require to display the container
   * panel
   */
  angular
    .module('horizon.dashboard.container.paymentmethods', [
      'ngRoute',
      'horizon.dashboard.container.paymentmethods.actions',
      'horizon.dashboard.container.paymentmethods.details'
    ])
    .constant('horizon.dashboard.container.paymentmethods.events', events())
    .constant('horizon.dashboard.container.paymentmethods.validStates', validStates())
    .constant('horizon.dashboard.container.paymentmethods.resourceType', 'OS::Zun::Paymentmethod')
    .run(run)
    .config(config);

  /**
   * @ngdoc constant
   * @name horizon.dashboard.container.paymentmethods.events
   * @description A list of events used by Container
   * @returns {Object} Event constants
   */
  function events() {
    return {
      CREATE_SUCCESS: 'horizon.dashboard.container.paymentmethods.CREATE_SUCCESS',
      DELETE_SUCCESS: 'horizon.dashboard.container.paymentmethods.DELETE_SUCCESS'
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
    'horizon.dashboard.container.paymentmethods.basePath',
    'horizon.dashboard.container.paymentmethods.resourceType',
    'horizon.dashboard.container.paymentmethods.service'
  ];

  function run(registry, zun, basePath, resourceType, containerService) {
    registry.getResourceType(resourceType)
    .setNames(gettext('Account'), gettext('Payment Methods'))
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
      'label': gettext('Paymentmethod ID'),
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
      'id': {label: gettext('Paymentmethod ID'), filters: ['noValue'] },
      'user_id': {label: gettext('User ID'), filters: ['noValue'] },
      'payment_method_type': {label: gettext('Payment Method Type'), filters: ['noValue'] },
      'cc_first_name': {label: gettext('CC First Name'), filters: ['noValue'] },
      'cc_middle_name': {label: gettext('CC Middle Name'), filters: ['noValue'] },
      'cc_last_name': {label: gettext('CC Last Name'), filters: ['noValue'] },
      'cc_card_no': {label: gettext('CC Card NO'), filters: ['noValue'] },
      'cc_billing_address_line1': {label: gettext('CC Billing Address Line1'), filters: ['noValue'] },
      'cc_billing_address_line2': {label: gettext('CC Billing Address Line2'), filters: ['noValue'] },
      'cc_billing_address_line3': {label: gettext('CC Billing Address Line3'), filters: ['noValue'] },
      'cc_billing_address_apt_suite_no': {label: gettext('CC Billing Address APT Suite NO'), filters: ['noValue'] },
      'cc_city': {label: gettext('CC City'), filters: ['noValue'] },
      'cc_state': {label: gettext('CC State'), filters: ['noValue'] },
      'cc_zipcode': {label: gettext('CC Zipcode'), filters: ['noValue'] },
      'cc_country': {label: gettext('CC Country'), filters: ['noValue'] },
      'cc_expiration_date': {label: gettext('CC Expiration Date'), filters: ['noValue'] },
      'pp_email': {label: gettext('PP Email'), filters: ['noValue'] },
      'displayname': {label: gettext('Displayname'), filters: ['noValue'] },
      'cc_cvv': {label: gettext('CC CVV'), filters: ['noValue'] }
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
    var path = $windowProvider.$get().STATIC_URL + 'dashboard/container/paymentmethods/';
    $provide.constant('horizon.dashboard.container.paymentmethods.basePath', path);
    $routeProvider.when('/admin/container/paymentmethods', {
      templateUrl: path + 'panel.html'
    });
  }
})();
