app.controller('DataCtrl', ['$scope','DataRes','ResTool',
  function($scope,DataRes,ResTool) {
  	ResTool.httpGetWithWorkspace(DataRes.isShowDataPanel, {}, {})
        .then(function(data) {
          if (data.data.code == "501") {
            $scope.isShowDataMngPanel = false;
          } else {
            $scope.isShowDataMngPanel = true;
          }
        }, function(err) {
          $scope.isShowDataMngPanel = false;
        });
}]);