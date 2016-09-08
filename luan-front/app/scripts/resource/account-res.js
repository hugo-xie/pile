angular.module('luna')
    .factory('AccountRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    'ngInject';
  return {
    account: function (headers) {
        return $resource(BASE_URL + '/account/:id', {
          id: '@id'
        }, {
          get: {
            method: 'GET',
            headers: headers
          },
          post: {
            method: 'POST',
            headers: headers
          },
          put: {
            method: 'PUT',
            headers: headers
          }
        });
      },
      accountMobile: function (headers) {
        return $resource(BASE_URL + '/account/mobile/:mobile', {
          mobile: '@mobile'
        }, {
          get: {
            method: 'GET',
            headers: headers
          },
          put: {
            method: 'PUT',
            headers: headers
          }
        });
      },
      accountSms: function (headers) {
        return $resource(BASE_URL + '/account/sms', {}, {
          get: {
            method: 'GET',
            headers: headers
          },
          post: {
            method: 'POST',
            headers: headers
          }
        });
      },
      accountPassword: function (headers) {
        return $resource(BASE_URL + '/account/password', {}, {
          post: {
            method: 'POST',
            headers: headers
          },
          put: {
            method: 'PUT',
            headers: headers
          }
        });
      },
      accountPasswordSms: function (headers) {
        return $resource(BASE_URL + '/account/password/sms', {}, {
          post: {
            method: 'POST',
            headers: headers
          },
          get: {
            method: 'GET',
            headers: headers
          }
        });
      },
      accountAuthentication: function (headers) {
        return $resource(BASE_URL + '/v1_0/login', {}, {
          post: {
            method: 'POST',
            headers: headers
          },
          get: {
            method: 'GET',
            headers: headers
          },
          delete: {
            method: 'DELETE',
            headers: headers
          }
        });
      },
      accountProfile: function (headers) {
        return $resource(BASE_URL + '/account/profile', {}, {
          get: {
            method: 'GET',
            headers: headers
          },
          put: {
            method: 'PUT',
            headers: headers
          }
        });
      },
      accountCompany: function (headers) {
        return $resource(BASE_URL + '/account/company', {}, {
          get: {
            method: 'GET',
            headers: headers
          },
          put: {
            method: 'PUT',
            headers: headers
          }
        });
      },
      accountIcon: function (headers) {
        return $resource(BASE_URL + '/account/icon/:attachId', {
          attachId: '@attachId'
        }, {
          put: {
            method: 'PUT',
            headers: headers
          }
        });
      },
      accountProfileSetting: function(headers){
        return $resource(BASE_URL + '/account/profile/setting', {}, {
          put: {
            method: 'PUT',
            headers: headers
          }
        });
      }
  };        
}])