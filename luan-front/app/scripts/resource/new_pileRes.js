angular.module('luna')
  .factory('newPileRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
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
      return $resource(BASE_URL+'/v1_0/pile_app/list', {
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
    newpile:function(headers){
      return $resource(BASE_URL+'/v1_0/pile/create', {
      }, {
         post: {
            method: 'POST',
            headers: headers
          },
      });
    },
    editpile:function(headers){
      return $resource(BASE_URL+'/v1_0/pile/edit/:id', {
        id:'@id'
      }, {
         post: {
            method: 'POST',
            headers: headers
          },
      })
    }
  };
}])