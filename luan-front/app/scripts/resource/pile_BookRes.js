angular.module('luna')
  .factory('pileBookRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    return {
    deleteBook: function (headers){
      return $resource(BASE_URL+'/v1_0/book/cancel/:id', {
        id:'@id'
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
    getall:function(headers){
      return $resource(BASE_URL+'/v1_0/book/list', {
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    }
  };
}])