angular.module('luna')
  .factory('parameterRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    return {
    getall:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_parameter/list', {
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
    newparameter:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_parameter/add', {
      }, {
         post: {
            method: 'POST',
            headers: headers
          },
      });
    },
    deleteparameter:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_parameter/delete/:id', {
        id:'@id'
      }, {
         get: {
            method: 'GET',
            headers: headers
          },
      });
    },
    editparameter:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_parameter/edit', {
        
      }, {
         post: {
            method: 'POST',
            headers: headers
          },
      })
    },
     updateparameter:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_parameter/update/:id', {
        id:'@id'
      }, {
         get: {
            method: 'GET',
            headers: headers
          },
      })
    },
    getversion:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_parameter/getVersion', {
        
      }, {
         get: {
            method: 'GET',
            headers: headers
          },
      })
    },
  };
}])