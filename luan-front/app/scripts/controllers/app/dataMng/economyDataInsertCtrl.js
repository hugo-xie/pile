'use strict';
app.controller('EconomyDataInsertCtrl', 
    ['$scope','ResTool','DataRes','ToasterTool', function($scope, ResTool, DataRes,ToasterTool) { //这里注入的顺序不能变
	var now = (new Date()).getFullYear();
	$scope.fourYear = [now-1,now,now+1,now+2,now+3];
	//用电 整体
	$scope.powerTotalSelectYear = (new Date()).getFullYear()-1;
	$scope.powerTotalPowerValue = null;
	$scope.powerTotalGdpValue = null;
	$scope.submitPowerTotal = function() {
		if (!$scope.powerTotalPowerValue || !$scope.powerTotalGdpValue) {
			ToasterTool.warning("空值警告");
			return;
		}
		var powerTotalBody = {
			"year": $scope.powerTotalSelectYear,
			"powerValue": $scope.powerTotalPowerValue,
			"gdpValue": $scope.powerTotalGdpValue
		};
		var PowerTotalPromise = ResTool.httpPost(DataRes.PowerTotal,{},powerTotalBody,{});
		PowerTotalPromise.then(function(data) {
			if (data.success) {
				ToasterTool.success("录入数据成功！");
			}else {
				ToasterTool.error("失败!");
			}
		}, function(err) {
			ToasterTool.error(err.message);
		});
	};
	//用电 行业
	$scope.powerIndustrySelectYear = (new Date()).getFullYear()-1+"";
	$scope.powerIndustrySelectQuarter = "1";
	$scope.powerIndustrySelected = "3001";
	$scope.powerIndustryPowerValue = null;
	$scope.powerIndustryGdpValue = null;

}]);