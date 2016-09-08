angular.module('luna')
  .factory('pileDeleteRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    return {
    deletepile: function (headers){
      return $resource(BASE_URL+'/v1_0/pile/delete/:id', {
        id:'@id'
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
    openpile: function (headers){
      return $resource(BASE_URL+'/v1_0/pile/edit/work_time', {
      }, {
        post: {
          method: 'POST',
          headers: headers
        },
      });
    }
  };
}])