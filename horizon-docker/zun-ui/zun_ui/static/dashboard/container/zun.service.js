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

  function ZunAPI(apiService, toast, gettext) {
    var usersPath = '/api/zun/users/';
    var providerregionsPath = '/api/zun/providerregions/';
    var providersPath = '/api/zun/providers/';

    var carriersPath = '/api/zun/carriers/';
    var containersPath = '/api/zun/containers/';
    var imagesPath = '/api/zun/images/';
    var service = {
      createUser: createUser,
      getUser: getUser,
      getUsers: getUsers,
      deleteUser: deleteUser,
      deleteUsers: deleteUsers,
      updateUser: updateUser,

      createProviderregion: createProviderregion,
      getProviderregion: getProviderregion,
      getProviderregions: getProviderregions,
      deleteProviderregion: deleteProviderregion,
      deleteProviderregions: deleteProviderregions,
      updateProviderregion: updateProviderregion,

      createProvider: createProvider,
      getProvider: getProvider,
      getProviders: getProviders,
      deleteProvider: deleteProvider,
      deleteProviders: deleteProviders,
      updateProvider: updateProvider,

      createCarrier: createCarrier,
      getCarrier: getCarrier,
      getCarriers: getCarriers,
      deleteCarrier: deleteCarrier,
      deleteCarriers: deleteCarriers,
      updateCarrier: updateCarrier,
      createContainer: createContainer,
      updateContainer: updateContainer,
      getContainer: getContainer,
      getContainers: getContainers,
      deleteContainer: deleteContainer,
      deleteContainers: deleteContainers,
      deleteContainerForce: deleteContainerForce,
      startContainer: startContainer,
      stopContainer: stopContainer,
      logsContainer: logsContainer,
      restartContainer: restartContainer,
      pauseContainer: pauseContainer,
      unpauseContainer: unpauseContainer,
      executeContainer: executeContainer,
      killContainer: killContainer,
      pullImage: pullImage,
      getImages: getImages
    };

    return service;

    ///////////////////
    //   Providers   //
    ///////////////////
    function createProvider(params) {
      var msg = gettext(params);
      return apiService.post(providersPath, params).error(error(msg));
    }
    function getProviders() {
      var msg = gettext('Unable to retrieve the Providers.');
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

    ///////////////
    // Carriers //
    ///////////////
    function createCarrier(params) {
      var msg = gettext(params);
      return apiService.post(carriersPath, params).error(error(msg));
    }
    function getCarriers() {
      var msg = gettext('Unable to retrieve the Carriers.');
      return apiService.get(carriersPath).error(error(msg));
    }
    function getCarrier(id) {
      var msg = gettext('Unable to retrieve the Carrier.');
      return apiService.get(carriersPath + id).error(error(msg));
    }
    function updateCarrier(id, params) {
      var msg = gettext('Unable to update Carrier.');
      return apiService.patch(carriersPath + id, params).error(error(msg));
    }
    function deleteCarrier(id, suppressError) {
      var promise = apiService.delete(carriersPath, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete the Carrier with id: %(id)s');
        toastService.add('error', interpolate(msg, { id: id }, true));
      });
    }
    // FIXME(shu-mutou): Unused for batch-delete in Horizon framework in Feb, 2016.
    function deleteCarriers(ids) {
      var msg = gettext('Unable to delete the Carriers.');
      return apiService.delete(carriersPath, ids).error(error(msg));
    }
    ///////////////
    // Containers //
    ///////////////

    function createContainer(params) {
      var msg = gettext(params);
      return apiService.post(containersPath, params).error(error(msg));
    }

    function updateContainer(id, params) {
      var msg = gettext('Unable to update Container.');
      return apiService.patch(containersPath + id, params).error(error(msg));
    }

    function getContainer(id) {
      var msg = gettext('Unable to retrieve the Container.');
      return apiService.get(containersPath + id).error(error(msg));
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
      var promise = apiService.delete(containersPath + id, [id]);
      return suppressError ? promise : promise.error(function() {
        var msg = gettext('Unable to delete forcely the Container with id: %(id)s');
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
        toast.add('error', message);
      };
    }
  }
}());
