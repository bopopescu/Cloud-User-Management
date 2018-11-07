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
  "use strict";

  angular
    .module("horizon.dashboard.container.users")
    .factory("horizon.dashboard.container.users.workflow", workflow);

  workflow.$inject = [
    "horizon.app.core.openstack-service-api.neutron",
    "horizon.dashboard.container.basePath",
    "horizon.framework.util.i18n.gettext",
    "horizon.framework.widgets.metadata.tree.service"
  ];

  function workflow(neutron, basePath, gettext, treeService) {
    var workflow = {
      init: init
    };

    function init(action, title, submitText) {
      var push = Array.prototype.push;
      var schema, form, model;
      var imageDrivers = [
        {value: "docker", name: gettext("Docker Hub")},
        {value: "glance", name: gettext("Glance")}
      ];
      /*var displaynamesList = [
        {value: "JASON", name: gettext("JASON")},
        {value: "LICHAO", name: gettext("LICHAO")}
      ];*/
      var imagePullPolicies = [
        {value: "", name: gettext("Select policy.")},
        {value: "ifnotpresent", name: gettext("If not present")},
        {value: "always", name: gettext("Always")},
        {value: "never", name: gettext("Never")}
      ];
      var restartPolicies = [
        {value: "", name: gettext("Select policy.")},
        {value: "no", name: gettext("No")},
        {value: "on-failure", name: gettext("On failure")},
        {value: "always", name: gettext("Always")},
        {value: "unless-stopped", name: gettext("Unless Stopped")}
      ];

      // schema
      schema = {
        type: "object",
        properties: {
          // info
          id: {
            title: gettext("User ID"),
            type: "string"
          },
          user_name: {
            title: gettext("User Name"),
            type: "string",
            pattern: "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
          },
          last_name: {
            title: gettext("Last Name"),
            type: "string"
          },
          first_name: {
            title: gettext("First Name"),
            type: "string"
          },
          middle_name: {
            title: gettext("Middle Name"),
            type: "string"
          },
          password: {
            title: gettext("Password"),
            type: "string"
          },
          account_status: {
            title: gettext("Account Status"),
            type: "string"
          },
          failed_attempt: {
            title: gettext("Failed Attempt"),
            type: "string"
          },
          last_login_method: {
            title: gettext("Last Login Method"),
            type: "string"
          },
          current_user_charge_tier: {
            title: gettext("Current User Charge Tier"),
            type: "string"
          },
          admin_ind: {
            title: gettext("Admin IND"),
            type: "string"
          },
          displayname: {
            title: gettext("Displayname"),
            type: "string"
          },
          passreset_url: {
            title: gettext("Passoword Reset URL"),
            type: "string"
          },
          activation_url: {
            title: gettext("Activation URL"),
            type: "string"
          },
          activation_expir_date: {
            title: gettext("Activation Expiration Date"),
            type: "string"
          },
          passreset_expir_date: {
            title: gettext("Password Reset Expiration Date"),
            type: "string"
          },
          last_login_time: {
            title: gettext("Last Login Time"),
            type: "string"
          },
          last_success_login_ip: {
            title: gettext("Last Success Login IP"),
            type: "string"
          },
          last_failed_login_ip: {
            title: gettext("Last Failed Login IP"),
            type: "string"
          },
          run: {
            title: gettext("Start container after creation"),
            type: "boolean"
          }
        }
      };
      // form
      form = [
        {
          type: "tabs",
          tabs: [
            {
              title: gettext("Users"),
              help: basePath + "users/actions/workflow/info.help.html",
              type: "section",
              htmlClass: "row",
              items: [
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "user_name",
                      placeholder: gettext("Name of the container to create."),
                      required: true,
                      validationMessage: "Please input valid email address."
                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "last_name",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "first_name",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "middle_name",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "password",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "account_status",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "failed_attempt",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "last_login_method",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "current_user_charge_tier",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "admin_ind",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                /*{
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "displayname",
                      placeholder: gettext("Name of the container to create."),
                      //readonly: action === "update",
                      required: true
                    }
                  ]
                },*/
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "passreset_url",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "activation_url",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "activation_expir_date",
                      placeholder: gettext(new Date)

                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "passreset_expir_date",
                      placeholder: gettext(new Date)

                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "last_login_time",
                      placeholder: gettext(new Date)

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "last_success_login_ip",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
                {
                  type:"section",
                  htmlClass:"col-xs-6",
                  items: [
                    {
                      key: "last_failed_login_ip",
                      placeholder: gettext("Name of the container to create."),

                    }
                  ]
                },
              ]
            }
          ]
        }
      ];
      // model
      model = {
        // info
        id: "",
        user_name: "",
        last_name: "",
        first_name: "",
        middle_name: "",
        password: "",
        account_status: "",
        failed_attempt: "",
        last_login_method: "",
        current_user_charge_tier: "",
        admin_ind: "",
        displayname: "",
        passreset_url: "",
        activation_url: "",
        activation_expir_date: "",
        passreset_expir_date: "",
        last_login_time: "",
        last_success_login_ip: "",
        last_failed_login_ip: "",
        run: true,
        // spec
      };

      // get available neutron networks and ports
      getNetworks();
      function getNetworks() {
        return neutron.getNetworks().then(onGetNetworks).then(getPorts);
      }

      function onGetNetworks(response) {
        push.apply(model.availableNetworks,
          response.data.items.filter(function(network) {
            return network.subnets.length > 0;
          }));
        return response;
      }

      function getPorts(networks) {
        networks.data.items.forEach(function(network) {
          return neutron.getPorts({network_id: network.id}).then(
            function(ports) {
              onGetPorts(ports, network);
            }
          );
        });
      }

      function onGetPorts(ports, network) {
        ports.data.items.forEach(function(port) {
          // no device_owner means that the port can be attached
          if (port.device_owner === "" && port.admin_state === "UP") {
            port.subnet_names = getPortSubnets(port, network.subnets);
            port.network_name = network.name;
            model.availablePorts.push(port);
          }
        });
      }

      // helper function to return an object of IP:NAME pairs for subnet mapping
      function getPortSubnets(port, subnets) {
        var subnetNames = {};
        port.fixed_ips.forEach(function (ip) {
          subnets.forEach(function (subnet) {
            if (ip.subnet_id === subnet.id) {
              subnetNames[ip.ip_address] = subnet.name;
            }
          });
        });
        return subnetNames;
      }

      var config = {
        title: title,
        submitText: submitText,
        schema: schema,
        form: form,
        model: model
      };

      return config;
    }

    return workflow;
  }
})();
