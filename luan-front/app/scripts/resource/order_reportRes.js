angular.module('luna')
  .factory('oderreportRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    return {
    dealreport: function (headers){
      return $resource(BASE_URL+'/v1_0/report/handled', {
      }, {
        post: {
          method: 'POST',
          headers: headers
        },
      });
    },
    getall:function(headers){
      return $resource(BASE_URL+'/v1_0/report/list', {
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
  };
}])