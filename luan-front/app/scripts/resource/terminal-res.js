angular.module('luna')
  .factory('terminalRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
    return {
    getall: function (headers){
      return $resource(BASE_URL+'/v1_0/terminal_image/list', {
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
    upload:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_image/add', {
      }, {
        post: {
          method: 'POST',
          headers: headers
        },
      });
    },
    deleteterminal:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_image/delete/:id', {
        id:'@id'
      }, {
        get: {
          method: 'GET',
          headers: headers
        },
      });
    },
    updateterminal:function(headers){
      return $resource(BASE_URL+'/v1_0/terminal_image/upgrade/all', {

      }, {
        get:{
          method:'GET',
          headers:headers
        }
      })
    },
  };
}])