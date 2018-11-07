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
    .module("horizon.dashboard.container.statements")
    .factory("horizon.dashboard.container.statements.workflow", workflow);

  workflow.$inject = [
    "horizon.app.core.openstack-service-api.zun",
    "horizon.app.core.openstack-service-api.neutron",
    "horizon.dashboard.container.basePath",
    "horizon.framework.util.i18n.gettext",
    "horizon.framework.widgets.metadata.tree.service"
  ];

  function workflow(zun, neutron, basePath, gettext, treeService) {
    var workflow = {
      init: init
    };

    function init(action, title, submitText) {

      var displaynamesList = [];
      if(displaynamesList.length == 0){
        queryUsers();
      }

      function queryUsers(){
        zun.getUsers().then(modifyUsersResponse);

        function modifyUsersResponse(response) {
            var res = {data: {items: response.data.items.map(modifyItem)}};
            var data = res["data"];
            var items = data["items"];
            var array = [];
            var i;
            for(i=0; i<items.length; i++){
                var displayname = items[i]["displayname"];
                var uuid = items[i]["id"];
                var obj = {
                      value: uuid + '~' + gettext(displayname),
                      name: gettext(displayname)
                };
                array.push(obj);
                //alert(JSON.stringify(array));
            }
            form[0].tabs[0].items[5].items[0].titleMap = array;
            //displaynamesList = array;
           // alert(JSON.stringify(displaynamesList) + "hehehehehe!");

            function modifyItem(item) {
                var timestamp = new Date();
                item.trackBy = item.id.concat(timestamp.getTime());
                return item;
            }
        }
      }

      var push = Array.prototype.push;
      var schema, form, model;
      var imageDrivers = [
        {value: "docker", name: gettext("Docker Hub")},
        {value: "glance", name: gettext("Glance")}
      ];
      /*var displaynamesList = [
        {value: "AWS", name: gettext("Amazon AWS")},
        {value: "GCE", name: gettext("Google GCE")}
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
            title: gettext("Statement ID"),
            type: "string"
          },
          user_id: {
            title: gettext("User ID"),
            type: "string"
          },
          previous_balance: {
            title: gettext("Previous Balance"),
            type: "string"
          },

          billing_begin_date: {
            title: gettext("Billing Begin Date"),
            type: "string"
          },
          /*begin_date_display:{
            title: gettext("Begin Date Display"),
            type: "string"
          },*/
          billing_end_date: {
            title: gettext("Billing End Date"),
            type: "string"
          },
          /*end_date_display:{
            title: gettext("End Date Display"),
            type: "string"
          },*/

          billing_charge_amount: {
            title: gettext("Billing Charge Amount"),
            type: "string"
          },
          current_balance: {
            title: gettext("Current Balance"),
            type: "string"
          },
          displayname: {
            title: gettext("Displayname"),
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
              title: gettext("Statements"),
              help: basePath + "statements/actions/workflow/info.help.html",
              type: "section",
              htmlClass: "row",
              items: [
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "previous_balance",
                      placeholder: gettext("name of the statement account"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "billing_charge_amount",
                      placeholder: gettext("access key"),

                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "billing_begin_date",
                      placeholder: gettext(new Date)
                      //title: gettext("Billing Begin Date"),
                      //type: "date",
                      /*onChange: function() {
                        form[0].tabs[0].items[3].items[0].placeholder = model.billing_begin_date;
                        alert(model.billing_begin_date);
                      }*/
                    }
                  ]
                },
                /*{
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "begin_date_display",
                      placeholder: gettext("begin date display"),
                      //value: ""
                    }
                  ]
                },*/
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "billing_end_date",
                      placeholder: gettext(new Date)
                      //title: gettext("Billing End Date"),
                      //type: "date",
                      /*onChange: function() {
                        form[0].tabs[0].items[5].items[0].placeholder = model.billing_end_date;
                        alert(model.billing_end_date);
                      }*/
                    }
                  ]
                },
                /*{
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "end_date_display",
                      placeholder: gettext("end date display"),
                      //value: ""
                    }
                  ]
                },*/
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "current_balance",
                      placeholder: gettext("access key"),

                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "displayname",
                      type: "select",
                      titleMap: displaynamesList,
                      //readonly: action === "update",
                      required: true
                    }
                  ]
                }
              ]
            }
          ]
        }
      ];
      // model
      model = {
        // info
        id: "",
        user_id: "",
        previous_balance: "",
        billing_begin_date: "",
        billing_end_date: "",
        billing_charge_amount: "",
        current_balance: "",
        displayname: "",
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
