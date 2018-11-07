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
   * @name horizon.dashboard.container.instances.update.service
   * @description Service for the container update modal
   */
  angular
    .module('horizon.dashboard.container.instances')
    .factory('horizon.dashboard.container.instances.update.service', updateService);

  updateService.$inject = [
    '$q',
    'horizon.app.core.openstack-service-api.policy',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.instances.resourceType',
    'horizon.dashboard.container.instances.validStates',
    'horizon.dashboard.container.instances.workflow',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.framework.util.q.extensions',
    'horizon.framework.widgets.form.ModalFormService',
    'horizon.framework.widgets.toast.service'
  ];

  function updateService(
    $q, policy, zun, resourceType, validStates, workflow,
    actionResult, gettext, $qExtensions, modal, toast
  ) {
    var message = {
      success: gettext('Account %s was successfully updated.')
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

    function perform(selected) {
      var title, submitText;
      title = gettext('Update Instance');
      submitText = gettext('Update');
      var config = workflow.init('update', title, submitText);
      config.model.id = selected.id;

      // load current data
      zun.getInstance(selected.id).then(onLoad);
      function onLoad(response) {
        config.model.id = response.data.id
          ? response.data.id : "";
        config.model.user_id = response.data.user_id
          ? response.data.user_id : "";
        config.model.instance_type_id = response.data.instance_type_id
          ? response.data.instance_type_id : "";
        config.model.provider_vm_id = response.data.provider_vm_id
          ? response.data.provider_vm_id : "";
        config.model.current_status = response.data.current_status
          ? response.data.current_status : "";
        config.model.current_status_time = response.data.current_status_time
          ? response.data.current_status_time : "";
        config.model.create_time = response.data.create_time
          ? response.data.create_time : "";

        var arr = response.data.displayname.split("_");
        var res = response.data.user_id + "~" + arr[1];
        config.model.displayname = res ? res : "";

        var arr2 = response.data.displayname2.split("_");
        var res2 = response.data.instance_type_id + "~" + arr2[1] + "_" + arr2[2] + "_" + arr2[3];
        config.model.displayname2 = res2 ? res2 : "";

        var arr3 = response.data.displayname3.split("_");
        var res3 = response.data.provider_vm_id + "~" + arr3[1] + "_" + arr3[2] + "_" + arr3[3] + "_" + arr3[4] + "_" + arr3[5];
        config.model.displayname3 = res3 ? res3 : "";
      }

      return modal.open(config).then(submit);
    }

    function allowed(container) {
      return policy.ifAllowed({ rules: [['container', 'edit_container']] });
    }

    function submit(context) {
      var id = context.model.id;
      var arr = context.model.displayname.split("~");
      context.model.user_id=arr[0];
      context.model.displayname=context.model.current_status+"_"+arr[1];

      var arr2 = context.model.displayname2.split("~");
      context.model.instance_type_id=arr2[0];
      context.model.displayname2=context.model.current_status+"_"+arr2[1];

      var arr3 = context.model.displayname3.split("~");
      context.model.provider_vm_id=arr3[0];
      context.model.displayname3=context.model.current_status+"_"+arr3[1];
      context.model = cleanUpdateProperties(context.model);
      return zun.updateInstance(id, context.model).then(success);
    }

    function success(response) {
      response.data.id = response.data.uuid;
      toast.add('success', interpolate(message.success, [response.data.name]));
      var result = actionResult.getActionResult().updated(resourceType, response.data.name);
      return result.result;
    }

    function cleanUpdateProperties(model) {
      // Initially clean fields that don't have any value.
      // Not only "null", blank too.
      // only "cpu" and "memory" fields are editable.
      for (var key in model) {
        if (model.hasOwnProperty(key) && model[key] === null || model[key] === "" ||
            (key !== "displayname" && key !== "displayname2" && key !== "displayname3" && key !== "user_id" && key !== "instance_type_id"
              && key !== "provider_vm_id" && key !== "current_status" && key !== "current_status_time" && key !== "create_time")) {
          delete model[key];
        }
      }
      return model;
    }

    function hashToString(hash) {
      var str = "";
      for (var key in hash) {
        if (hash.hasOwnProperty(key)) {
          if (str.length > 0) {
            str += ",";
          }
          str += key + "=" + hash[key];
        }
      }
      return str;
    }
  }
})();
