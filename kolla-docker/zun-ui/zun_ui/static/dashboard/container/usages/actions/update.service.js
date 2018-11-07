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
   * @name horizon.dashboard.container.usages.update.service
   * @description Service for the container update modal
   */
  angular
    .module('horizon.dashboard.container.usages')
    .factory('horizon.dashboard.container.usages.update.service', updateService);

  updateService.$inject = [
    '$q',
    'horizon.app.core.openstack-service-api.policy',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.usages.resourceType',
    'horizon.dashboard.container.usages.validStates',
    'horizon.dashboard.container.usages.workflow',
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
      title = gettext('Update Usage');
      submitText = gettext('Update');
      var config = workflow.init('update', title, submitText);
      config.model.id = selected.id;

      // load current data
      zun.getUsage(selected.id).then(onLoad);
      function onLoad(response) {
        config.model.id = response.data.id
          ? response.data.id : "";
        config.model.user_id = response.data.user_id
          ? response.data.user_id : "";
        config.model.instance_id = response.data.instance_id
          ? response.data.instance_id : "";
        config.model.compute_rate_id = response.data.compute_rate_id
          ? response.data.compute_rate_id : "";
        config.model.storage_rate_id = response.data.storage_rate_id
          ? response.data.storage_rate_id : "";
        config.model.start_time = response.data.start_time
          ? response.data.start_time : "";
        config.model.stop_time = response.data.stop_time
          ? response.data.stop_time : "";
        config.model.duration = response.data.duration
          ? response.data.duration : "";
        config.model.cost = response.data.cost
          ? response.data.cost : "";

        var arr = response.data.displayname.split("_");
        var res = response.data.user_id + "~" + arr[1];
        config.model.displayname = res ? res : "";

        var arr2 = response.data.displayname2.split("_");
        var res2 = response.data.instance_id + "~" + arr2[1] + "_" + arr2[2] + "_" + arr2[3] + "_" + arr2[4] + "_" + arr2[5]
         + "_" + arr2[6] + "_" + arr2[7] + "_" + arr2[8] + "_" + arr2[9] + "_" + arr2[10] + "_" + arr2[11] + "_" + arr2[12];
        config.model.displayname2 = res2 ? res2 : "";

        var arr3 = response.data.displayname3.split("_");
        var res3 = response.data.compute_rate_id + "~" + arr3[1] + "_" + arr3[2] + "_" + arr3[3] + "_" + arr3[4];
        config.model.displayname3 = res3 ? res3 : "";

        var arr4 = response.data.displayname4.split("_");
        var res4 = response.data.storage_rate_id + "~" + arr4[1] + "_" + arr4[2] + "_" + arr4[3];
        config.model.displayname4 = res4 ? res4 : "";
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
      context.model.displayname=context.model.duration+"_"+arr[1];

      var arr2 = context.model.displayname2.split("~");
      context.model.instance_id=arr2[0];
      context.model.displayname2=context.model.duration+"_"+arr2[1];

      var arr3 = context.model.displayname3.split("~");
      context.model.compute_rate_id=arr3[0];
      context.model.displayname3=context.model.duration+"_"+arr3[1];

      var arr4 = context.model.displayname4.split("~");
      context.model.storage_rate_id=arr4[0];
      context.model.displayname4=context.model.duration+"_"+arr4[1];
      context.model = cleanUpdateProperties(context.model);
      return zun.updateUsage(id, context.model).then(success);
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
            (key !== "displayname" && key !== "displayname2" && key !== "displayname3" && key !== "displayname4" && key !== "user_id" && key !== "instance_id"
              && key !== "compute_rate_id" && key !== "storage_rate_id" && key !== "start_time" && key !== "stop_time" && key !== "duration" && key !== "cost")) {
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
