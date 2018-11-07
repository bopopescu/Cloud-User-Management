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
   * @name horizon.dashboard.container.instances.create.service
   * @description Service for the container create modal
   */
  angular
    .module('horizon.dashboard.container.instances')
    .factory('horizon.dashboard.container.instances.create.service', createService);

  createService.$inject = [
    'horizon.app.core.openstack-service-api.policy',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.instances.resourceType',
    'horizon.dashboard.container.instances.workflow',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.framework.util.q.extensions',
    'horizon.framework.widgets.form.ModalFormService',
    'horizon.framework.widgets.toast.service'
  ];

  function createService(
    policy, zun, resourceType, workflow,
    actionResult, gettext, $qExtensions, modal, toast
  ) {
    var message = {
      success: gettext('Account %s was successfully created.')
    };

    var service = {
      initAction: initAction,
      perform: perform,
      allowed: allowed
    };

    return service;

    //////////////

    function initAction() {
    }

    function perform() {
      var title, submitText;
      title = gettext('Add Instance');
      submitText = gettext('Create');
      var config = workflow.init('create', title, submitText);
      return modal.open(config).then(submit);
    }

    function allowed() {
      return policy.ifAllowed({ rules: [['container', 'add_container']] });
    }

    function submit(context) {
      var arr = context.model.displayname.split("~");
      context.model.user_id=arr[0];
      context.model.displayname=context.model.current_status+"_"+arr[1];

      var arr2 = context.model.displayname2.split("~");
      context.model.instance_type_id=arr2[0];
      context.model.displayname2=context.model.current_status+"_"+arr2[1];

      var arr3 = context.model.displayname3.split("~");
      context.model.provider_vm_id=arr3[0];
      context.model.displayname3=context.model.current_status+"_"+arr3[1];

      context.model = cleanNullProperties(context.model);
      return zun.createInstance(context.model).then(success);
    }

    function success(response) {
      response.data.id = response.data.uuid;
      toast.add('success', interpolate(message.success, [response.data.name]));
      var result = actionResult.getActionResult().created(resourceType, response.data.name);
      return result.result;
    }

    function cleanNullProperties(model) {
      // Initially clean fields that don't have any value.
      // Not only "null", blank too.
      for (var key in model) {
        if (model.hasOwnProperty(key) && model[key] === null || model[key] === "" ||
            key === "tabs") {
          delete model[key];
        }
      }
      return model;
    }

    function setNetworksAndPorts(model) {
      // pull out the ids from the security groups objects
      var nets = [];
      model.networks.forEach(function(network) {
        nets.push({network: network.id});
      });
      model.ports.forEach(function(port) {
        nets.push({port: port.id});
      });
      return nets;
    }

    function setSecurityGroups(model) {
      // pull out the ids from the security groups objects
      var securityGroups = [];
      model.security_groups.forEach(function(securityGroup) {
        securityGroups.push(securityGroup.name);
      });
      return securityGroups;
    }

    function setSchedulerHints(model) {
      var schedulerHints = {};
      if (model.hintsTree) {
        var hints = model.hintsTree.getExisting();
        if (!angular.equals({}, hints)) {
          angular.forEach(hints, function(value, key) {
            schedulerHints[key] = value + '';
          });
        }
      }
      return schedulerHints;
    }
  }
})();
