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
   * @name horizon.dashboard.container.providers.update.service
   * @description Service for the container update modal
   */
  angular
    .module('horizon.dashboard.container.providers')
    .factory('horizon.dashboard.container.providers.update.service', updateService);

  updateService.$inject = [
    '$q',
    'horizon.app.core.openstack-service-api.policy',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.providers.resourceType',
    'horizon.dashboard.container.providers.validStates',
    'horizon.dashboard.container.providers.workflow',
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
      title = gettext('Update Account');
      submitText = gettext('Update');
      var config = workflow.init('update', title, submitText);
      config.model.id = selected.id;

      // load current data
      zun.getProvider(selected.id).then(onLoad);
      function onLoad(response) {
        config.model.id = response.data.id
          ? response.data.id : "";
        config.model.provider = response.data.provider
          ? response.data.provider : "";
      }

      return modal.open(config).then(submit);
    }

    function allowed(container) {
      return policy.ifAllowed({ rules: [['container', 'edit_container']] });
    }

    function submit(context) {
      var id = context.model.id;
      context.model = cleanUpdateProperties(context.model);
      return zun.updateProvider(id, context.model).then(success);
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
            (key !== "provider")) {
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
