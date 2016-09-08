// angular.module('luna')
//     .factory('DataRes', ['$resource','BASE_URL', function($resource,BASE_URL) {
//     'ngInject';
//   return {
//       PowerTotal: function (headers) {
//         return $resource(BASE_URL + '/data/population/structure/total', {}, {
//           post: {
//             method: 'POST',
//             headers: headers
//           },
//         });
//       },
//       },
//   };        
// }]);