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
   * @name horizon.dashboard.container.paymentmethods.create.service
   * @description Service for the container create modal
   */
  angular
    .module('horizon.dashboard.container.paymentmethods')
    .factory('horizon.dashboard.container.paymentmethods.create.service', createService);

  createService.$inject = [
    'horizon.app.core.openstack-service-api.policy',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.paymentmethods.resourceType',
    'horizon.dashboard.container.paymentmethods.workflow',
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
      title = gettext('Add Payment Method');
      submitText = gettext('Create');
      var config = workflow.init('create', title, submitText, '');
      return modal.open(config).then(submit);
    }

    function allowed() {
      return policy.ifAllowed({ rules: [['container', 'add_container']] });
    }

    /*function validateCardNo(elementValue){
      var cardNoPattern = /^[0-9]{13,16}$/;
      return cardNoPattern.test(elementValue);
    }

    function validateCardCVV(elementValue){
      var cardCVVPattern = /^[0-9]{3,4}$/;
      return cardCVVPattern.test(elementValue);
    }

    function validateEmail(elementValue){
      var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
      return emailPattern.test(elementValue);
    }

    function validateExpDate(elementValue){
      var month = elementValue.substring(0,2);
      var year = elementValue.substring(2);
      var month_now = String(new Date().getMonth());
      var year_now = String(new Date().getFullYear()).substring(2);

      //alert(month);
      //alert(year);
      //alert(month_now);
      //alert(year_now);

      if(year - year_now < 0){
        //alert("year is invalid");
        return false;
      }

      if(year == year_now){
        if(month - month_now < 0){
          //alert("month is invalid");
          return false;
        }
      }
      return true;
    }*/

    function submit(context) {
      context.model.cc_expiration_date = context.model.cc_expiration_month + context.model.cc_expiration_year;
      //alert(context.model.cc_expiration_month);
      //alert(context.model.cc_expiration_year);
      //alert(context.model.cc_expiration_date);
      //alert("3 line into submit");

      /*if(!validateCardNo(context.model.cc_card_no)){
        alert ("Please input valid Credit Card Number");
      }
      else if(!validateCardCVV(context.model.cc_cvv)){
        alert ("Please input valid Credit Card CVV");
      }
      else if(!validateEmail(context.model.pp_email)){
        alert ("PP Email must be in valid email format!");
      }
      if(!validateExpDate(context.model.cc_expiration_date)){
        alert("Please input valid Credit Card Expiration Date")
      }*/

      var arr = context.model.displayname.split("~");
      var cc_card_no_length = context.model.cc_card_no.length;
      var cc_card_no_last4 = context.model.cc_card_no[cc_card_no_length-4]+context.model.cc_card_no[cc_card_no_length-3]+
                             context.model.cc_card_no[cc_card_no_length-2]+context.model.cc_card_no[cc_card_no_length-1];
      context.model.user_id=arr[0];
      context.model.displayname=arr[1]+"_"+context.model.payment_method_type+"_"+cc_card_no_last4;
      context.model = cleanNullProperties(context.model);
      return zun.createPaymentmethod(context.model).then(success);
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
            key === "tabs" || (key !== "user_id" && key !== "payment_method_type" && key !== "cc_first_name" && key !== "cc_middle_name"
             && key !== "cc_last_name" && key !== "cc_card_no" && key !== "cc_billing_address_line1"
              && key !== "cc_billing_address_line2" && key !== "cc_billing_address_line3" && key !== "cc_cvv"
               && key !== "cc_billing_address_apt_suite_no" && key !== "cc_city" && key !== "cc_state" && key !== "cc_zipcode"
                && key !== "cc_country" && key !== "cc_expiration_date" && key !== "pp_email" && key !== "displayname")) {
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
