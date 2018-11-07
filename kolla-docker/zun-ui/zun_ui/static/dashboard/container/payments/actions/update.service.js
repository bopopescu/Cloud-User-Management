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
   * @name horizon.dashboard.container.payments.update.service
   * @description Service for the container update modal
   */
  angular
    .module('horizon.dashboard.container.payments')
    .factory('horizon.dashboard.container.payments.update.service', updateService);

  updateService.$inject = [
    '$q',
    'horizon.app.core.openstack-service-api.policy',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.payments.resourceType',
    'horizon.dashboard.container.payments.validStates',
    'horizon.dashboard.container.payments.workflow',
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
      title = gettext('Update Payment');
      submitText = gettext('Update');
      var config = workflow.init('update', title, submitText);
      config.model.id = selected.id;

      // load current data
      zun.getPayment(selected.id).then(onLoad);
      function onLoad(response) {
        config.model.id = response.data.id
          ? response.data.id : "";
        config.model.statement_id = response.data.statement_id
          ? response.data.statement_id : "";
        config.model.payment_method_id = response.data.payment_method_id
          ? response.data.payment_method_id : "";
        config.model.amount = response.data.amount
          ? response.data.amount : "";
        config.model.payment_date = response.data.payment_date
          ? response.data.payment_date : "";
        config.model.status = response.data.status
          ? response.data.status : "";

        var arr = response.data.displayname.split("_");
        var res = response.data.statement_id + "~" + arr[1] + "_" + arr[2];
        config.model.displayname = res ? res : "";

        var arr2 = response.data.displayname2.split("_");
        var res2 = response.data.payment_method_id + "~" + arr2[1] + "_" + arr2[2] + "_" + arr2[3];
        config.model.displayname2 = res2 ? res2 : "";
      }

      return modal.open(config).then(submit);
    }

    function allowed(container) {
      return policy.ifAllowed({ rules: [['container', 'edit_container']] });
    }

    function submit(context) {
      var id = context.model.id;
      var arr = context.model.displayname.split("~");
      context.model.statement_id=arr[0];
      context.model.displayname=context.model.amount+"_"+arr[1];

      var arr2 = context.model.displayname2.split("~");
      context.model.payment_method_id=arr2[0];
      context.model.displayname2=context.model.amount+"_"+arr2[1];

      context.model = cleanUpdateProperties(context.model);
      return zun.updatePayment(id, context.model).then(success);
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
            (key !== "displayname" && key !== "displayname2" && key !== "statement_id" && key !== "payment_method_id" && key !== "amount" && key !== "payment_date" && key !== "status")) {
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
