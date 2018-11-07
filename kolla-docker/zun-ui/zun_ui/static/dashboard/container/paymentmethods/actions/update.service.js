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
   * @name horizon.dashboard.container.paymentmethods.update.service
   * @description Service for the container update modal
   */
  angular
    .module('horizon.dashboard.container.paymentmethods')
    .factory('horizon.dashboard.container.paymentmethods.update.service', updateService);

  updateService.$inject = [
    '$q',
    'horizon.app.core.openstack-service-api.policy',
    'horizon.app.core.openstack-service-api.zun',
    'horizon.dashboard.container.paymentmethods.resourceType',
    'horizon.dashboard.container.paymentmethods.validStates',
    'horizon.dashboard.container.paymentmethods.workflow',
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
      title = gettext('Update Payment Method');
      submitText = gettext('Update');
      var config = workflow.init('update', title, submitText, selected.id);
      config.model.id = selected.id;

      // load current data
      zun.getPaymentmethod(selected.id).then(onLoad);
      function onLoad(response) {
        config.model.id = response.data.id
          ? response.data.id : "";
        config.model.user_id = response.data.user_id
          ? response.data.user_id : "";
        config.model.payment_method_type = response.data.payment_method_type
          ? response.data.payment_method_type : "";
        config.model.cc_first_name = response.data.cc_first_name
          ? response.data.cc_first_name : "";
        config.model.cc_middle_name = response.data.cc_middle_name
          ? response.data.cc_middle_name : "";
        config.model.cc_last_name = response.data.cc_last_name
          ? response.data.cc_last_name : "";
        config.model.cc_card_no = response.data.cc_card_no
          ? response.data.cc_card_no : "";
        config.model.cc_billing_address_line1 = response.data.cc_billing_address_line1
          ? response.data.cc_billing_address_line1 : "";
        config.model.cc_billing_address_line2 = response.data.cc_billing_address_line2
          ? response.data.cc_billing_address_line2 : "";
        config.model.cc_billing_address_line3 = response.data.cc_billing_address_line3
          ? response.data.cc_billing_address_line3 : "";
        config.model.cc_billing_address_apt_suite_no = response.data.cc_billing_address_apt_suite_no
          ? response.data.cc_billing_address_apt_suite_no : "";
        config.model.cc_city = response.data.cc_city
          ? response.data.cc_city : "";
        config.model.cc_state = response.data.cc_state
          ? response.data.cc_state : "";
        config.model.cc_zipcode = response.data.cc_zipcode
          ? response.data.cc_zipcode : "";
        config.model.cc_country = response.data.cc_country
          ? response.data.cc_country : "";

        config.model.cc_expiration_date = response.data.cc_expiration_date
          ? response.data.cc_expiration_date : "";

        config.model.cc_expiration_month = response.data.cc_expiration_date.substring(0,2)
          ? response.data.cc_expiration_date.substring(0,2) : "";
        config.model.cc_expiration_year = response.data.cc_expiration_date.substring(2)
          ? response.data.cc_expiration_date.substring(2) : "";

        config.model.pp_email = response.data.pp_email
          ? response.data.pp_email : "";
        config.model.cc_cvv = response.data.cc_cvv
          ? response.data.cc_cvv : "";

        var arr = response.data.displayname.split("_");
        var res = response.data.user_id + "~" + arr[0];
        // trim the response of displayname first to fit the dropdown format
        config.model.displayname = res ? res : "";

        //alert(res);
      }

      return modal.open(config).then(submit);
    }

    function allowed(container) {
      return policy.ifAllowed({ rules: [['container', 'edit_container']] });
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

      /*if(!validateCardNo(context.model.cc_card_no)){
        alert ("Please input valid Credit Card Number");
      }
      else if(!validateCardCVV(context.model.cc_cvv)){
        alert ("Please input valid Credit Card CVV");
      }
      else if(!validateEmail(context.model.pp_email)){
        alert ("PP Email must be in valid email format");
      }
      if(!validateExpDate(context.model.cc_expiration_date)){
        alert("Please input valid Credit Card Expiration Date")
      }*/

      var cc_card_no_length = context.model.cc_card_no.length;
      var cc_card_no_last4 = context.model.cc_card_no[cc_card_no_length-4]+context.model.cc_card_no[cc_card_no_length-3]+
                             context.model.cc_card_no[cc_card_no_length-2]+context.model.cc_card_no[cc_card_no_length-1];
      var id = context.model.id;
      var arr = context.model.displayname.split("~");
      context.model.user_id=arr[0];
      context.model.displayname=arr[1]+"_"+context.model.payment_method_type+"_"+cc_card_no_last4;
      context.model = cleanUpdateProperties(context.model);
      return zun.updatePaymentmethod(id, context.model).then(success);

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
            (key !== "user_id" && key !== "payment_method_type" && key !== "cc_first_name" && key !== "cc_middle_name"
             && key !== "cc_last_name" && key !== "cc_card_no" && key !== "cc_billing_address_line1"
              && key !== "cc_billing_address_line2" && key !== "cc_billing_address_line3" && key !== "cc_cvv"
               && key !== "cc_billing_address_apt_suite_no" && key !== "cc_city" && key !== "cc_state" && key !== "cc_zipcode"
                && key !== "cc_country" && key !== "cc_expiration_date" && key !== "pp_email" && key !== "displayname")) {
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
