/**
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
(function () {
  'use strict';

  angular
    .module('horizon.app.core.openstack-service-api')
    .factory('horizon.app.core.openstack-service-api.zun', ZunAPI);

  ZunAPI.$inject = [
    'horizon.framework.util.http.service',
    'horizon.framework.widgets.toast.service',
    'horizon.framework.util.i18n.gettext'
  ];

  function ZunAPI(apiService, toastService, gettext) {
    var containersPath = '/api/zun/containers/';
    var imagesPath = '/api/zun/images/';

    var providersPath = '/api/zun/providers/';
    var usersPath = '/api/zun/users/';
    var providerregionsPath = '/api/zun/providerregions/';
    var providervmsPath = '/api/zun/providervms/';
    var provideraccountsPath = '/api/zun/provideraccounts/';
    var paymentsPath = '/api/zun/payments/';
    var paymentmethodsPath = '/api/zun/paymentmethods/';
    var usagesPath = '/api/zun/usages/';
    var storageratesPath = '/api/zun/storagerates/';
    var computeratesPath = '/api/zun/computerates/';
    var instancesPath = '/api/zun/instances/';
    var instancetypesPath = '/api/zun/instancetypes/';
    var statementsPath = '/api/zun/statements/';

    var service = {

      createUser: createUser,
      getUser: getUser,
      getUsers: getUsers,
      deleteUser: deleteUser,
      deleteUsers: deleteUsers,
      updateUser: updateUser,

      createProvider: createProvider,
      getProvider: getProvider,
      getProviders: getProviders,
      deleteProvider: deleteProvider,
      deleteProviders: deleteProviders,
      updateProvider: updateProvider,

      createProviderregion: createProviderregion,
      getProviderregion: getProviderregion,
      getProviderregions: getProviderregions,
      deleteProviderregion: deleteProviderregion,
      deleteProviderregions: deleteProviderregions,
      updateProviderregion: updateProviderregion,

      createProvidervm: createProvidervm,
      getProvidervm: getProvidervm,
      getProvidervms: getProvidervms,
      deleteProvidervm: deleteProvidervm,
      deleteProvidervms: deleteProvidervms,
      updateProvidervm: updateProvidervm,

      createProvideraccount: createProvideraccount,
      getProvideraccount: getProvideraccount,
      getProvideraccounts: getProvideraccounts,
      deleteProvideraccount: deleteProvideraccount,
      deleteProvideraccounts: deleteProvideraccounts,
      updateProvideraccount: updateProvideraccount,

      createStatement: createStatement,
      getStatement: getStatement,
      getStatements: getStatements,
      deleteStatement: deleteStatement,
      deleteStatements: deleteStatements,
      updateStatement: updateStatement,

      createPayment: createPayment,
      getPayment: getPayment,
      getPayments: getPayments,
      deletePayment: deletePayment,
      deletePayments: deletePayments,
      updatePayment: updatePayment,

      createPaymentmethod: createPaymentmethod,
      getPaymentmethod: getPaymentmethod,
      getPaymentmethods: getPaymentmethods,
      deletePaymentmethod: deletePaymentmethod,
      deletePaymentmethods: deletePaymentmethods,
      updatePaymentmethod: updatePaymentmethod,

      createInstance: createInstance,
      getInstance: getInstance,
      getInstances: getInstances,
      deleteInstance: deleteInstance,
      deleteInstances: deleteInstances,
      updateInstance: updateInstance,

      createInstancetype: createInstancetype,
      getInstancetype: getInstancetype,
      getInstancetypes: getInstancetypes,
      deleteInstancetype: deleteInstancetype,
      deleteInstancetypes: deleteInstancetypes,
      updateInstancetype: updateInstancetype,

      createUsage: createUsage,
      getUsage: getUsage,
      getUsages: getUsages,
      deleteUsage: deleteUsage,
      deleteUsages: deleteUsages,
      updateUsage: updateUsage,

      createComputerate: createComputerate,
      getComputerate: getComputerate,
      getComputerates: getComputerates,
      deleteComputerate: deleteComputerate,
      deleteComputerates: deleteComputerates,
      updateComputerate: updateComputerate,

      createStoragerate: createStoragerate,
      getStoragerate: getStoragerate,
      getStoragerates: getStoragerates,
      deleteStoragerate: deleteStoragerate,
      deleteStoragerates: deleteStoragerates,
      updateStoragerate: updateStoragerate,

      createContainer: createContainer,
      updateContainer: updateContainer,
      getContainer: getContainer,
      getContainers: getContainers,
      deleteContainer: deleteContainer,
      deleteContainers: deleteContainers,
      deleteContainerForce: deleteContainerForce,
      deleteContainerStop: deleteContainerStop,
      startContainer: startContainer,
      stopContainer: stopContainer,
      logsContainer: logsContainer,
      restartContainer: restartContainer,
      pauseContainer: pauseContainer,
      unpauseContainer: unpauseContainer,
      executeContainer: executeContainer,
      killContainer: killContainer,
      resizeContainer: resizeContainer,
      attachNetwork: attachNetwork,
      detachNetwork: detachNetwork,
      pullImage: pullImage,
      getImages: getImages
    };

    return service;

    ///////////////
    //   Users   //
    ///////////////
    function createUser(params) {
      var msg = gettext(params);
      return apiService.post(usersPath, params).error(error(msg));
    }
    function getUsers() {
      var msg = gettext('Unable to retrieve the Users.');
      return apiService.get(usersPath).error(error(msg));
    }
    function getUser(id) {
      var msg = gettext('Unable to retrieve the User.');
      return apiService.get(usersPath + id).error(error(msg));
    }
    function updateUser(id, params) {
      var msg = gettext('Unable to update User.');
      return apiService.patch(usersPath + id, params).error(error(msg));
    }
    function deleteUser(id, suppressError) {
      var promise = apiService.delete(usersPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the User with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteUsers(ids) {
      var msg = gettext('Unable to delete the User.');
      return apiService.delete(usersPath, ids).error(error(msg));
    }

    ///////////////////
    //   Providers   //
    ///////////////////
    function createProvider(params) {
      var msg = gettext(params);
      return apiService.post(providersPath, params).error(error(msg));
    }
    function getProviders() {
      var msg = gettext('Unable to retrieve the Providers.');
      // alert(JSON.stringify(apiService.get(providersPath).error(error(msg))));
      return apiService.get(providersPath).error(error(msg));
    }
    function getProvider(id) {
      var msg = gettext('Unable to retrieve the Provider.');
      return apiService.get(providersPath + id).error(error(msg));
    }
    function updateProvider(id, params) {
      var msg = gettext('Unable to update Provider.');
      return apiService.patch(providersPath + id, params).error(error(msg));
    }
    function deleteProvider(id, suppressError) {
      var promise = apiService.delete(providersPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Provider with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteProviders(ids) {
      var msg = gettext('Unable to delete the Provider.');
      return apiService.delete(providersPath, ids).error(error(msg));
    }

    ///////////////////
    //Providerregions//
    ///////////////////
    function createProviderregion(params) {
      var msg = gettext(params);
      return apiService.post(providerregionsPath, params).error(error(msg));
    }
    function getProviderregions() {
      var msg = gettext('Unable to retrieve the Providerregions.');
      return apiService.get(providerregionsPath).error(error(msg));
    }
    function getProviderregion(id) {
      var msg = gettext('Unable to retrieve the Providerregion.');
      return apiService.get(providerregionsPath + id).error(error(msg));
    }
    function updateProviderregion(id, params) {
      var msg = gettext('Unable to update Providerregion.');
      return apiService.patch(providerregionsPath + id, params).error(error(msg));
    }
    function deleteProviderregion(id, suppressError) {
      var promise = apiService.delete(providerregionsPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Providerregion with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteProviderregions(ids) {
      var msg = gettext('Unable to delete the Providerregion.');
      return apiService.delete(providerregionsPath, ids).error(error(msg));
    }

    ///////////////////
    //  Providervms  //
    ///////////////////
    function createProvidervm(params) {
      var msg = gettext(params);
      return apiService.post(providervmsPath, params).error(error(msg));
    }
    function getProvidervms() {
      var msg = gettext('Unable to retrieve the Providervms.');
      return apiService.get(providervmsPath).error(error(msg));
    }
    function getProvidervm(id) {
      var msg = gettext('Unable to retrieve the Providervm.');
      return apiService.get(providervmsPath + id).error(error(msg));
    }
    function updateProvidervm(id, params) {
      var msg = gettext('Unable to update Providervm.');
      return apiService.patch(providervmsPath + id, params).error(error(msg));
    }
    function deleteProvidervm(id, suppressError) {
      var promise = apiService.delete(providervmsPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Providervm with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteProvidervms(ids) {
      var msg = gettext('Unable to delete the Providervm.');
      return apiService.delete(providervmsPath, ids).error(error(msg));
    }

    ////////////////////
    //Provideraccounts//
    ////////////////////
    function createProvideraccount(params) {
      var msg = gettext(params);
      return apiService.post(provideraccountsPath, params).error(error(msg));
    }
    function getProvideraccounts() {
      var msg = gettext('Unable to retrieve the Provideraccounts.');
      return apiService.get(provideraccountsPath).error(error(msg));
    }
    function getProvideraccount(id) {
      var msg = gettext('Unable to retrieve the Provideraccount.');
      return apiService.get(provideraccountsPath + id).error(error(msg));
    }
    function updateProvideraccount(id, params) {
      var msg = gettext('Unable to update Provideraccount.');
      return apiService.patch(provideraccountsPath + id, params).error(error(msg));
    }
    function deleteProvideraccount(id, suppressError) {
      var promise = apiService.delete(provideraccountsPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Provideraccount with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteProvideraccounts(ids) {
      var msg = gettext('Unable to delete the Provideraccount.');
      return apiService.delete(provideraccountsPath, ids).error(error(msg));
    }

    ///////////////////
    //   Instances   //
    ///////////////////
    function createInstance(params) {
      var msg = gettext(params);
      return apiService.post(instancesPath, params).error(error(msg));
    }
    function getInstances() {
      var msg = gettext('Unable to retrieve the Instances.');
      return apiService.get(instancesPath).error(error(msg));
    }
    function getInstance(id) {
      var msg = gettext('Unable to retrieve the Instance.');
      return apiService.get(instancesPath + id).error(error(msg));
    }
    function updateInstance(id, params) {
      var msg = gettext('Unable to update Instance.');
      return apiService.patch(instancesPath + id, params).error(error(msg));
    }
    function deleteInstance(id, suppressError) {
      var promise = apiService.delete(instancesPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Instance with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteInstances(ids) {
      var msg = gettext('Unable to delete the Instance.');
      return apiService.delete(instancesPath, ids).error(error(msg));
    }

    ///////////////////
    //  Storagerates //
    ///////////////////
    function createStoragerate(params) {
      var msg = gettext(params);
      return apiService.post(storageratesPath, params).error(error(msg));
    }
    function getStoragerates() {
      var msg = gettext('Unable to retrieve the Storagerates.');
      return apiService.get(storageratesPath).error(error(msg));
    }
    function getStoragerate(id) {
      var msg = gettext('Unable to retrieve the Storagerate.');
      return apiService.get(storageratesPath + id).error(error(msg));
    }
    function updateStoragerate(id, params) {
      var msg = gettext('Unable to update Storagerate.');
      return apiService.patch(storageratesPath + id, params).error(error(msg));
    }
    function deleteStoragerate(id, suppressError) {
      var promise = apiService.delete(storageratesPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Storagerate with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteStoragerates(ids) {
      var msg = gettext('Unable to delete the Storagerate.');
      return apiService.delete(storageratesPath, ids).error(error(msg));
    }

    ///////////////////
    // Instancetypes //
    ///////////////////
    function createInstancetype(params) {
      var msg = gettext(params);
      return apiService.post(instancetypesPath, params).error(error(msg));
    }
    function getInstancetypes() {
      var msg = gettext('Unable to retrieve the Instancetypes.');
      return apiService.get(instancetypesPath).error(error(msg));
    }
    function getInstancetype(id) {
      var msg = gettext('Unable to retrieve the Instancetype.');
      return apiService.get(instancetypesPath + id).error(error(msg));
    }
    function updateInstancetype(id, params) {
      var msg = gettext('Unable to update Instancetype.');
      return apiService.patch(instancetypesPath + id, params).error(error(msg));
    }
    function deleteInstancetype(id, suppressError) {
      var promise = apiService.delete(instancetypesPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Instancetype with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteInstancetypes(ids) {
      var msg = gettext('Unable to delete the Instancetype.');
      return apiService.delete(instancetypesPath, ids).error(error(msg));
    }

    ///////////////////
    //     Usages    //
    ///////////////////
    function createUsage(params) {
      var msg = gettext(params);
      return apiService.post(usagesPath, params).error(error(msg));
    }
    function getUsages() {
      var msg = gettext('Unable to retrieve the Usages.');
      return apiService.get(usagesPath).error(error(msg));
    }
    function getUsage(id) {
      var msg = gettext('Unable to retrieve the Usage.');
      return apiService.get(usagesPath + id).error(error(msg));
    }
    function updateUsage(id, params) {
      var msg = gettext('Unable to update Usage.');
      return apiService.patch(usagesPath + id, params).error(error(msg));
    }
    function deleteUsage(id, suppressError) {
      var promise = apiService.delete(usagesPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Usage with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteUsages(ids) {
      var msg = gettext('Unable to delete the Usage.');
      return apiService.delete(usagesPath, ids).error(error(msg));
    }

    ///////////////////
    //   Statements  //
    ///////////////////
    function createStatement(params) {
      var msg = gettext(params);
      return apiService.post(statementsPath, params).error(error(msg));
    }
    function getStatements() {
      var msg = gettext('Unable to retrieve the Statements.');
      return apiService.get(statementsPath).error(error(msg));
    }
    function getStatement(id) {
      var msg = gettext('Unable to retrieve the Statement.');
      return apiService.get(statementsPath + id).error(error(msg));
    }
    function updateStatement(id, params) {
      var msg = gettext('Unable to update Statement.');
      return apiService.patch(statementsPath + id, params).error(error(msg));
    }
    function deleteStatement(id, suppressError) {
      var promise = apiService.delete(statementsPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Statement with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteStatements(ids) {
      var msg = gettext('Unable to delete the Statement.');
      return apiService.delete(statementsPath, ids).error(error(msg));
    }

    ///////////////////
    //  Computerates //
    ///////////////////
    function createComputerate(params) {
      var msg = gettext(params);
      return apiService.post(computeratesPath, params).error(error(msg));
    }
    function getComputerates() {
      var msg = gettext('Unable to retrieve the Computerates.');
      return apiService.get(computeratesPath).error(error(msg));
    }
    function getComputerate(id) {
      var msg = gettext('Unable to retrieve the Computerate.');
      return apiService.get(computeratesPath + id).error(error(msg));
    }
    function updateComputerate(id, params) {
      var msg = gettext('Unable to update Computerate.');
      return apiService.patch(computeratesPath + id, params).error(error(msg));
    }
    function deleteComputerate(id, suppressError) {
      var promise = apiService.delete(computeratesPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Computerate with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteComputerates(ids) {
      var msg = gettext('Unable to delete the Computerate.');
      return apiService.delete(computeratesPath, ids).error(error(msg));
    }

    ///////////////////
    //   Payments   //
    ///////////////////
    function createPayment(params) {
      var msg = gettext(params);
      return apiService.post(paymentsPath, params).error(error(msg));
    }
    function getPayments() {
      var msg = gettext('Unable to retrieve the Payments.');
      return apiService.get(paymentsPath).error(error(msg));
    }
    function getPayment(id) {
      var msg = gettext('Unable to retrieve the Payment.');
      return apiService.get(paymentsPath + id).error(error(msg));
    }
    function updatePayment(id, params) {
      var msg = gettext('Unable to update Payment.');
      return apiService.patch(paymentsPath + id, params).error(error(msg));
    }
    function deletePayment(id, suppressError) {
      var promise = apiService.delete(paymentsPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Payment with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deletePayments(ids) {
      var msg = gettext('Unable to delete the Payment.');
      return apiService.delete(paymentsPath, ids).error(error(msg));
    }

    ///////////////////
    // Paymentmethods//
    ///////////////////
    function createPaymentmethod(params) {
      var msg = gettext(params);
      return apiService.post(paymentmethodsPath, params).error(error(msg));
    }
    function getPaymentmethods() {
      var msg = gettext('Unable to retrieve the Paymentmethods.');
      return apiService.get(paymentmethodsPath).error(error(msg));
    }
    function getPaymentmethod(id) {
      var msg = gettext('Unable to retrieve the Paymentmethod.');
      return apiService.get(paymentmethodsPath + id).error(error(msg));
    }
    function updatePaymentmethod(id, params) {
      var msg = gettext('Unable to update Paymentmethod.');
      return apiService.patch(paymentmethodsPath + id, params).error(error(msg));
    }
    function deletePaymentmethod(id, suppressError) {
      var promise = apiService.delete(paymentmethodsPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Paymentmethod with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deletePaymentmethods(ids) {
      var msg = gettext('Unable to delete the Paymentmethod.');
      return apiService.delete(paymentmethodsPath, ids).error(error(msg));
    }

    ///////////////
    // Containers //
    ///////////////

    function createContainer(params) {
      var msg = gettext('Unable to create Container.');
      return apiService.post(containersPath, params).error(error(msg));
    }

    function updateContainer(id, params) {
      var msg = gettext('Unable to update Container.');
      return apiService.patch(containersPath + id, params).error(error(msg));
    }

    function getContainer(id, suppressError) {
      var promise = apiService.get(containersPath + id);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to retrieve the Container.');
        toastService.add('error', msg);
      });
    }

    function getContainers() {
      var msg = gettext('Unable to retrieve the Containers.');
      return apiService.get(containersPath).error(error(msg));
    }

    function deleteContainer(id, suppressError) {
      var promise = apiService.delete(containersPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Container with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }

    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteContainers(ids) {
      var msg = gettext('Unable to delete the Containers.');
      return apiService.delete(containersPath, ids).error(error(msg));
    }

    function deleteContainerForce(id, suppressError) {
      var promise = apiService.delete(containersPath + id + '/force', [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete forcely the Container with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }

    function deleteContainerStop(id, suppressError) {
      var promise = apiService.delete(containersPath + id + '/stop', [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to stop and delete the Container with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }

    function startContainer(id) {
      var msg = gettext('Unable to start Container.');
      return apiService.post(containersPath + id + '/start').error(error(msg));
    }

    function stopContainer(id, params) {
      var msg = gettext('Unable to stop Container.');
      return apiService.post(containersPath + id + '/stop', params).error(error(msg));
    }

    function logsContainer(id) {
      var msg = gettext('Unable to get logs of Container.');
      return apiService.get(containersPath + id + '/logs').error(error(msg));
    }

    function restartContainer(id, params) {
      var msg = gettext('Unable to restart Container.');
      return apiService.post(containersPath + id + '/restart', params).error(error(msg));
    }

    function pauseContainer(id) {
      var msg = gettext('Unable to pause Container');
      return apiService.post(containersPath + id + '/pause').error(error(msg));
    }

    function unpauseContainer(id) {
      var msg = gettext('Unable to unpause of Container.');
      return apiService.post(containersPath + id + '/unpause').error(error(msg));
    }

    function executeContainer(id, params) {
      var msg = gettext('Unable to execute the command.');
      return apiService.post(containersPath + id + '/execute', params).error(error(msg));
    }

    function killContainer(id, params) {
      var msg = gettext('Unable to send kill signal.');
      return apiService.post(containersPath + id + '/kill', params).error(error(msg));
    }

    function resizeContainer(id, params) {
      var msg = gettext('Unable to resize console.');
      return apiService.post(containersPath + id + '/resize', params).error(error(msg));
    }

    function attachNetwork(id, net) {
      var msg = gettext('Unable to attach network.');
      return apiService.post(containersPath + id + '/network_attach', {network: net})
        .error(error(msg));
    }

    function detachNetwork(id, net) {
      var msg = gettext('Unable to detach network.');
      return apiService.post(containersPath + id + '/network_detach', {network: net})
        .error(error(msg));
    }

    ////////////
    // Images //
    ////////////

    function pullImage(params) {
      var msg = gettext('Unable to pull Image.');
      return apiService.post(imagesPath, params).error(error(msg));
    }

    function getImages() {
      var msg = gettext('Unable to retrieve the Images.');
      return apiService.get(imagesPath).error(error(msg));
    }

    function error(message) {
      return function() {
        toastService.add('error', message);
      };
    }
  }
}());
