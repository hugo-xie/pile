app.controller('BookController', ['$scope','$stateParams','ResTool','SweetAlert','oderreportRes', function($scope,$stateParams,ResTool,SweetAlert,oderreportRes){
   $('#myDatepickerInput1').datepicker();
    $('#myDatepickerInput2').datepicker();
    $scope.accusation = function(){
    $('#accusationmodal').modal('show');
   };
   
   $scope.problem = function(){
    $('#accusationmodal').modal('hide');
    var test  = $('#test1').val();
     console.log(test); 
    swal("举报信息已提交", "", "success");
   };
    $scope.filterOptions = {
        filterText: "",
        useExternalFilter: true
       }; 
       $scope.totalServerItems = 0;
       $scope.pagingOptions = {
        pageSizes: [10, 20, 30],
        pageSize: 10,
        currentPage: 1
       }; 
       $scope.setPagingData = function(data, page, pageSize){ 
        var pagedData = data.rows.slice((page - 1) * pageSize, page * pageSize);
        $scope.myData = pagedData;
        $scope.totalServerItems = data.total;
        if (!$scope.$$phase) {
            $scope.$apply();
        }
     }; 
     $scope.getPagedDataAsync = function (pageSize, page) {        
                /*$http.get('jsonFiles/largeLoad.json').success(function (largeLoad) {
                    $scope.setPagingData(largeLoad,page,pageSize);
                }); */

                if ($('#myDatepickerInput1').val() == "") {
      $scope.start = null;
     }else{
       $scope.start = moment($('#myDatepickerInput1').val(),"MM-DD-YYYY").format("YYYY-MM-DD")+" "+"00:00:00";
     }
     if ($('#myDatepickerInput2').val() == "") {
      $scope.end = null;
     }else{
       $scope.end = moment($('#myDatepickerInput2').val(),"MM-DD-YYYY").format("YYYY-MM-DD")+" "+"00:00:00";
     }
        ResTool.httpGetWithToken(oderreportRes.getall,{limit:1000,report_start:$scope.start,report_end:$scope.end,id:$scope.seacherid},{}).then(
          function(rc){
            for(var i =0;i<rc.rows.length;i++){
              if (rc.rows[i].handled == true) {
                rc.rows[i].handled = "已处理";
              }else if (rc.rows[i].handled == false) {
                rc.rows[i].handled = "尚未处理";
              }
            }
            console.log(rc.rows);
            $scope.setPagingData(rc,page,pageSize);
          }
          )
    };
    $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    $scope.$watch('pagingOptions', function (newVal, oldVal) {
        if (newVal !== oldVal && newVal.currentPage !== oldVal.currentPage) {
          $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
        }
    }, true);
    $scope.$watch('filterOptions', function (newVal, oldVal) {
        if (newVal !== oldVal) {
          $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
        }
    }, true);
    $scope.mySelections=[];
     $scope.gridOptions = {
        data: 'myData',
        enablePaging: true,
        showFooter: true,
        totalServerItems: 'totalServerItems',
        pagingOptions: $scope.pagingOptions,
        filterOptions: $scope.filterOptions,
        selectedItems:$scope.mySelections,
        enablePinning: true,
        multiSelect:false,
        i18n:'zh-cn',
        columnDefs: [{field: 'user_id', displayName: '用户ID'},
                     {field:'id',displayName:'举报信息编号'},
                     {field:'dt',displayName:'时间'},
                     {field:'evidence',displayName:'证据'},
                     {field:'comment',displayName:'建议'},
                     {field:'handled', displayName:'是否处理', cellTemplate: '<div ng-class="{green: row.getProperty(col.field) > 30}"><div class="ngCellText">{{row.getProperty(col.field)}}</div></div>'}]
    };

  $scope.deelreport = function(){
          
          $("#repotid").val($scope.mySelections[0].id);
          $("#repotertime").val($scope.mySelections[0].dt);
           $("#reporterid").val($scope.mySelections[0].user_id);
          $('#accusationmodal').modal('show');
        };
$scope.seach = function(){
  $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
}
$scope.submitreport = function(){
         var promise = ResTool.httpPostWithToken(oderreportRes.dealreport,{},{
            plate:$("#test1").val(),
            deduct_score:$scope.deletescore,
            bonus_score:$scope.plusscore,
            comment:$("#problemdetail").val(),
            report_id:$scope.mySelections[0].id,
            report_user_id:$scope.mySelections[0].user_id
          },{});
         var body = {
           plate:$("#test1").val(),
            deduct_score:$scope.deletescore,
            bonus_score:$scope.plusscore,
            comment:"well",
            report_id:$scope.mySelections[0].id,
            report_user_id:$scope.mySelections[0].user_id
         }
         $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
         promise.then(function(rc){
           swal(rc.msg, "", "info");
            console.log(body);
         });
          $('#accusationmodal').modal('hide');
        };


}])