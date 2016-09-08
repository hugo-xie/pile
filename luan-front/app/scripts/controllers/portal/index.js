'use strict';

app.controller('IndexController', ['$scope', function($scope) {
  $scope.imagesrc="images/"+2+".png";
  var i =1;
  
  var carousel = function(i){
    if (i<6) {
      $scope.imagesrc="images/"+i+".png";
      i=i+1;
    }else{
      i=1;
      $scope.imagesrc="images/"+i+".png";
    }
   
  };
 self.setInterval(carousel(),500);

}]);
