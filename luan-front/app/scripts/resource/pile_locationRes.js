angular.module('luna')
    .factory('locationRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
        return {
            getTotal: function (headers){
                return $resource(BASE_URL+'/v1_0/pile/list', {}, {
                    get: {
                        method: 'GET',
                        headers: headers
                    },
                });
            }
        };
    }])