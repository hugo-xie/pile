'use strict';
app.controller('PopulationDataInsertCtrl', 
    ['$scope','ResTool','DataRes','ToasterTool', function($scope, ResTool, DataRes,ToasterTool) { //这里注入的顺序不能变
	var now = (new Date()).getFullYear();
	$scope.fourYear = [now-1,now,now+1,now+2,now+3];
}]);