angular.module('luna')
    .factory('PopulationRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
        return {
            getEmployInsuranceSchoolList: function (headers){
                return $resource(BASE_URL+'/population/populationEmployInsuranceData/list', {}, {
                    get: {
                        method: 'GET',
                        headers: headers
                    },
                });
            },
            getLaborGdpRelationPreData: function (headers){
                return $resource(BASE_URL+'/population/laborGdpRelationPreData/list', {}, {
                    get: {
                        method: 'GET',
                        headers: headers
                    },
                });
            },
            getPopulationStructurePreData: function (headers){
                return $resource(BASE_URL+'/population/populationStructurePreData/list', {}, {
                    get: {
                        method: 'GET',
                        headers: headers
                    },
                });
            },
            getSumPopulationData: function (headers){
                return $resource(BASE_URL+'/population/sumPopulationData/list', {}, {
                    get: {
                        method: 'GET',
                        headers: headers
                    },
                });
            },
            getBirthrateData: function (headers){
                return $resource(BASE_URL+'/population/birthrateData/list', {}, {
                    get: {
                        method: 'GET',
                        headers: headers
                    },
                });
            },
        };
    }])