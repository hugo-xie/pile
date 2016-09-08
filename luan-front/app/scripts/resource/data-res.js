angular.module('luna')
    .factory('DataRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    'ngInject';
  return {
      PowerTotal: function (headers) {
        return $resource(BASE_URL + '/data/economy/power/total', {}, {
          post: {
            method: 'POST',
            headers: headers
          },
        });
      },
      PowerIndustry: function (headers) {
        return $resource(BASE_URL + '/data/economy/power/industry', {}, {
          post: {
            method: 'POST',
            headers: headers
          },
        });
      },
      PowerEnterprise: function (headers) {
        return $resource(BASE_URL + '/data/economy/power/enterprise', {}, {
          post: {
            method: 'POST',
            headers: headers
          },
        });
      },
      isShowDataPanel: function (headers) {
        return $resource(BASE_URL + '/data/isshow', {}, {
          get: {
            method: 'GET',
            headers: headers
          },
        });
      },
  };        
}]);