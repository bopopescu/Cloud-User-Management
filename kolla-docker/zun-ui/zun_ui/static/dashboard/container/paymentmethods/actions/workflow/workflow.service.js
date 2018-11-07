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
    .module("horizon.dashboard.container.paymentmethods")
    .factory("horizon.dashboard.container.paymentmethods.workflow", workflow);

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

    function init(action, title, submitText, selectedid) {

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
                // this is a dropdown with value: uuid~displayname and name: displayname
            }

            //alert(JSON.stringify(array));

            form[0].tabs[0].items[16].items[0].titleMap = array;

            //displaynamesList = array;
            // alert(JSON.stringify(displaynamesList) + "hahahahaha!");

            function modifyItem(item) {
                var timestamp = new Date();
                item.trackBy = item.id.concat(timestamp.getTime());
                return item;
            }
        }
      }

      var cc_statenamesList = [];
      if(selectedid !== ''){
        zun.getPaymentmethod(selectedid).then(getState);

        function getState(response) {
            var countryname = response.data.cc_country;
            //alert(countryname);
            var state = eval(countryname);
            form[0].tabs[0].items[10].items[0].titleMap = state;
            cc_statenamesList = state;
            //alert(JSON.stringify(state));
        }
      }

      var push = Array.prototype.push;
      var schema, form, model;
      var imageDrivers = [
        {value: "docker", name: gettext("Docker Hub")},
        {value: "glance", name: gettext("Glance")}
      ];
      var cc_countrynamesList = [
        {value: "USA", name: gettext("USA")},
        {value: "CHINA", name: gettext("CHINA")}
      ];
      var USA = [
        {value: "TEXAS", name: gettext("TEXAS")},
        {value: "CALIFORNIA", name: gettext("CALIFORNIA")}
      ];
      var CHINA = [
        {value: "BEIJING", name: gettext("BEIJING")},
        {value: "SHANGHAI", name: gettext("SHANGHAI")}
      ];
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
      var payment_method_type = [
        {value: "Master", name: gettext("Master Card")},
        {value: "Visa", name: gettext("Visa Card")},
        {value: "Discover", name: gettext("Discover Card")}
      ];
      var cc_expiryearsList = [];
      var cc_expirmonthsList = [
        {value: "01", name: gettext("01")},
        {value: "02", name: gettext("02")},
        {value: "03", name: gettext("03")},
        {value: "04", name: gettext("04")},
        {value: "05", name: gettext("05")},
        {value: "06", name: gettext("06")},
        {value: "07", name: gettext("07")},
        {value: "08", name: gettext("08")},
        {value: "09", name: gettext("09")},
        {value: "10", name: gettext("10")},
        {value: "11", name: gettext("11")},
        {value: "12", name: gettext("12")}
      ];
      /*var cc_expiryearsList = [
        {value: "18", name: gettext("2018")},
        {value: "19", name: gettext("2019")},
        {value: "20", name: gettext("2020")},
        {value: "21", name: gettext("2021")},
        {value: "22", name: gettext("2022")},
        {value: "23", name: gettext("2023")},
        {value: "24", name: gettext("2024")},
        {value: "25", name: gettext("2025")},
        {value: "26", name: gettext("2026")},
        {value: "27", name: gettext("2027")},
        {value: "28", name: gettext("2028")},
        {value: "29", name: gettext("2029")}
      ];*/

      // schema
      schema = {
        type: "object",
        properties: {
          // info
          id: {
            title: gettext("Paymentmethod ID"),
            type: "string"
          },
          user_id: {
            title: gettext("User ID"),
            type: "string"
          },
          payment_method_type: {
            title: gettext("Payment Method Type"),
            //minLength: 1,
            //type: "string"
          },
          cc_first_name: {
            title: gettext("CC First Name"),
            type: "string"
          },
          cc_middle_name: {
            title: gettext("CC Middle Name"),
            type: "string"
          },
          cc_last_name: {
            title: gettext("CC Last Name"),
            type: "string"
          },
          cc_card_no: {
            title: gettext("CC Card NO"),
            type: "string",
            pattern: "^[0-9]{13,16}$"
          },
          cc_billing_address_line1: {
            title: gettext("CC Billing Address Line1"),
            type: "string"
          },
          cc_billing_address_line2: {
            title: gettext("CC Billing Address Line2"),
            type: "string"
          },
          cc_billing_address_line3: {
            title: gettext("CC Billing Address Line3"),
            type: "string"
          },
          cc_billing_address_apt_suite_no: {
            title: gettext("CC Billing Address APT Suite NO"),
            type: "string"
          },
          cc_city: {
            title: gettext("CC City"),
            type: "string"
          },
          cc_state: {
            title: gettext("CC State"),
            //type: "string"
          },
          cc_zipcode: {
            title: gettext("CC Zipcode"),
            type: "string"
          },
          cc_country: {
            title: gettext("CC Country"),
            //type: "string"
          },
          cc_expiration_date: {
            title: gettext("CC Expiration Date"),
            type: "string"
          },
          cc_expiration_month: {
            title: gettext("CC Expiration Month"),
            //minLength: 1,
            //type: "string"
          },
          cc_expiration_year: {
            title: gettext("CC Expiration Year"),
            //minLength: 1,
            //type: "string"
          },
          pp_email: {
            title: gettext("PP Email"),
            type: "string",
            pattern: "^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
          },
          displayname: {
            title: gettext("Displayname"),
            type: "string",
            //minLength: 1,
          },
          cc_cvv: {
            title: gettext("CC CVV"),
            type: "string",
            pattern: "^[0-9]{3,4}$"
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
              title: gettext("Payment Methods"),
              help: basePath + "paymentmethods/actions/workflow/info.help.html",
              type: "section",
              htmlClass: "row",
              items: [
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "payment_method_type",
                      title: gettext("Payment Method Type"),
                      type: "select",
                      titleMap: payment_method_type,
                      required: true

                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_first_name",
                      placeholder: gettext("e.g., aws access key id"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_middle_name",
                      placeholder: gettext("access key"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_last_name",
                      placeholder: gettext("access key"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_card_no",
                      placeholder: gettext("access key"),
                      required: true,
                      validationMessage: "Please input valid credit card number."
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_billing_address_line1",
                      placeholder: gettext("access key"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_billing_address_line2",
                      placeholder: gettext("access key"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_billing_address_line3",
                      placeholder: gettext("access key"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_billing_address_apt_suite_no",
                      placeholder: gettext("access key"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_country",
                      title: gettext("CC Country"),
                      type: "select",
                      titleMap: cc_countrynamesList,
                      //readonly: action === "update",
                      //required: true,
                      onChange: function() {
                        var countryname = model.cc_country;
                        form[0].tabs[0].items[10].items[0].titleMap = eval(countryname);
                        //cc_statenamesList = eval(countryname);
                      }
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_state",
                      title: gettext("CC State"),
                      type: "select",
                      titleMap: cc_statenamesList,
                      //readonly: action === "update",
                      //required: true
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_city",
                      placeholder: gettext("access key")
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_zipcode",
                      placeholder: gettext("access key"),
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-3",
                  items: [
                    {
                      key: "cc_expiration_month",
                      type: "select",
                      title: gettext("CC Expiration Month"),
                      titleMap: cc_expirmonthsList,
                      required: true
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-3",
                  items: [
                    {
                      key: "cc_expiration_year",
                      type: "select",
                      title: gettext("CC Expiration Year"),
                      titleMap: cc_expiryearsList,
                      required: true,
                      onChange: function() {
                        var cc_expiration_year = model.cc_expiration_year;
                        var year_now = new Date().getFullYear();
                        var month_now = new Date().getMonth() + 1;

                        if(cc_expiration_year == String(year_now).substring(2)){
                          var month_array = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"];
                          var array = [];
                          var i;
                          for(i=month_now; i<=12; i++){
                            if(String(i).length == 1){
                              var obj = {value: "0" + String(i), name: gettext(month_array[i-1])};
                            }
                            else{
                              var obj = {value: String(i), name: gettext(month_array[i-1])};
                            }
                            array.push(obj);
                          }
                          form[0].tabs[0].items[13].items[0].titleMap = array;
                        }
                        else{
                          /*var cc_expirmonthsList = [
                            {value: "01", name: gettext("January")},
                            {value: "02", name: gettext("February")},
                            {value: "03", name: gettext("March")},
                            {value: "04", name: gettext("April")},
                            {value: "05", name: gettext("May")},
                            {value: "06", name: gettext("June")},
                            {value: "07", name: gettext("July")},
                            {value: "08", name: gettext("August")},
                            {value: "09", name: gettext("September")},
                            {value: "10", name: gettext("October")},
                            {value: "11", name: gettext("November")},
                            {value: "12", name: gettext("December")}
                          ];*/
                          form[0].tabs[0].items[13].items[0].titleMap = cc_expirmonthsList;
                        }
                      }
                    }
                  ]
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "pp_email",
                      placeholder: gettext("access key"),
                      required: true,
                      validationMessage: "Please input valid email address."
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
                },
                {
                  type: "section",
                  htmlClass: "col-xs-6",
                  items: [
                    {
                      key: "cc_cvv",
                      placeholder: gettext("Last three digits located on the back of your card. For American Express the four digits found on the front side."),
                      required: true,
                      validationMessage: "Please input valid credit card cvv number."
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
        payment_method_type: "",
        cc_first_name: "",
        cc_middle_name: "",
        cc_last_name: "",
        cc_card_no: "",
        cc_billing_address_line1: "",
        cc_billing_address_line2: "",
        cc_billing_address_line3: "",
        cc_billing_address_apt_suite_no: "",
        cc_city: "",
        cc_state: "",
        cc_zipcode: "",
        cc_country: "",
        cc_expiration_date: "",
        cc_expiration_month: "",
        cc_expiration_year: "",
        pp_email: "",
        displayname: "",
        cc_cvv: "",
        run: true,
        // spec
      };

      if(cc_expiryearsList.length == 0){
        //alert("cc_expiryearsList.length == 0");
        get_cc_expiryearsList();
      }

      function get_cc_expiryearsList(){
        //alert("enter get_cc_expiryearsList");
        var year_now = new Date().getFullYear();
        //alert(year_now);
        var array = [];
        var i;
        for(i=0; i<10; i++){
          var obj = {value: String(year_now + i).substring(2), name: gettext(String(year_now + i))};
          array.push(obj);
        }
        //alert(JSON.stringify(array));
        form[0].tabs[0].items[14].items[0].titleMap = array;
      }

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
