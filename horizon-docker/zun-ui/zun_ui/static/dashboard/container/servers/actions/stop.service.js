/**
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use self file except in compliance with the License. You may obtain
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
   * @ngDoc factory
   * @name horizon.dashboard.container.servers.stop.service
   * @Description
   * Stop container.
   */
  angular
    .module('horizon.dashboard.container.servers')
    .factory('horizon.dashboard.container.servers.stop.service', stopService);

  stopService.$inject = [
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.servers.basePath',
    'horizon.dashboard.container.servers.resourceType',
    'horizon.dashboard.container.servers.validStates',
    'horizon.framework.util.actions.action-result.service',
    'horizon.framework.util.i18n.gettext',
    'horizon.framework.util.q.extensions',
    'horizon.framework.widgets.form.ModalFormService',
    'horizon.framework.widgets.toast.service'
  ];

  function stopService(
    zun, basePath, resourceType, validStates, actionResult, gettext, $qExtensions, modal, toast
  ) {
    // schema
    var schema = {
      type: "object",
      properties: {
        timeout: {
          title: gettext("Stop Container"),
          type: "number",
          minimum: 1
        }
      }
    };

    // form
    var form = [
      {
        type: 'section',
        htmlClass: 'row',
        items: [
          {
            type: 'section',
            htmlClass: 'col-sm-12',
            items: [
              {
                "key": "timeout",
                "placeholder": gettext("Specify a shutdown timeout in seconds. (default: 10)")
              }
            ]
          }
        ]
      }
    ];

    // model
    var model;

    var message = {
      success: gettext('Container %s was successfully stoped.')
    };

    var service = {
      initAction: initAction,
      allowed: allowed,
      perform: perform
    };

    return service;

    //////////////

    // include this function in your service
    // if you plan to emit events to the parent controller
    function initAction() {
    }

    function allowed(container) {
      return $qExtensions.booleanAsPromise(
        validStates.stop.indexOf(container.status) >= 0
      );
    }

    function perform(selected) {
      model = {
        id: selected.id,
        name: selected.name,
        timeout: null
      };
      // modal config
      var config = {
        "title": gettext('Stop Container'),
        "submitText": gettext('Stop'),
        "schema": schema,
        "form": form,
        "model": model
      };
      return modal.open(config).then(submit);

      function submit(context) {
        var id = context.model.id;
        var name = context.model.name;
        delete context.model.id;
        delete context.model.name;
        return zun.stopContainer(id, context.model).then(function() {
          toast.add('success', interpolate(message.success, [name]));
          var result = actionResult.getActionResult().updated(resourceType, id);
          return result.result;
        });
      }
    }
  }
})();
