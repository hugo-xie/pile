angular.module('luna')
  .factory('roleRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    return {
    uprole: function (headers){
      return $resource(BASE_URL+'/v1_0/user/allow_login/:id', {
        id:'@id'
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
    downrole: function (headers){
      return $resource(BASE_URL+'/v1_0/user/deny_login/:id', {
        id:'@id'
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
     adduser: function (headers){
      return $resource(BASE_URL+'/v1_0/user/add', {
        
      }, {
        post: {
          method: 'POST',
          headers: headers
        },
      });
    },
    getall:function(headers){
      return $resource(BASE_URL+'/v1_0/user/list', {
        
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    }
  };
}])