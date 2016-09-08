app.controller('PileController', ['$scope','$stateParams','ResTool','SweetAlert','pileBookRes','roleRes','AuthTool','$localStorage', function($scope,$stateParams,ResTool,SweetAlert,pileBookRes,roleRes,AuthTool,$localStorage){
    $scope.loginUser = AuthTool.getLoginUser();
      
      $scope.currWorkspace = AuthTool.getCurrWorkspace();
       if ($scope.loginUser == "admin") {
        $scope.isadmin =true;
       }
    $('#myDatepickerInput1').datepicker();
    $('#myDatepickerInput2').datepicker();
$scope.filterOptions = {
        filterText: "",
        useExternalFilter: true
       }; 
       $scope.totalServerItems = 0;
       $scope.pagingOptions = {
        pageSizes: [10, 20, 30],
        pageSize: 20,
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
     var parameter = {
      limit:200
     } 
    
     
     $scope.getPagedDataAsync = function (pageSize, page) {        
                /*$http.get('jsonFiles/largeLoad.json').success(function (largeLoad) {
                    $scope.setPagingData(largeLoad,page,pageSize);
                }); */
                $scope.start = null;
                $scope.end = null;
     if ($('#myDatepickerInput1').val() == "") {
      $scope.start = null;
     }else{
       $scope.start = moment($('#myDatepickerInput1').val(),"MM-DD-YYYY").format("YYYY-MM-DD");
     }
     if ($('#myDatepickerInput2').val() == "") {
      $scope.end = null;
     }else{
       $scope.end = moment($('#myDatepickerInput2').val(),"MM-DD-YYYY").format("YYYY-MM-DD");
     }
        ResTool.httpGetWithToken(pileBookRes.getall,{limit:20000,id:$scope.seacherid,book_start_start:$scope.start,book_start_end:$scope.end,user_id:$scope.userid,pile_id:$scope.pileid},{}).then(
          function(rc){
            for(var i =0;i<rc.rows.length;i++){
              if (rc.rows[i].status == 0) {
                rc.rows[i].status = "用户尚未付款";
              }else if (rc.rows[i].status == 1){
                rc.rows[i].status = "用户已付款";
              }else if (rc.rows[i].status == 2){
                rc.rows[i].status = "桩主接受订单";
              }else if (rc.rows[i].status == 3){
                rc.rows[i].status = "桩主拒绝订单";
              }else if (rc.rows[i].status == 4){
                rc.rows[i].status = "用户开始充电";
              }else if (rc.rows[i].status == 5){
                rc.rows[i].status = "用户完成充电";
              }else if (rc.rows[i].status == 6){
                rc.rows[i].status = "用户尚未使用";
              }else if (rc.rows[i].status == 7){
                rc.rows[i].status = "订单取消";
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
          $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
        }
    }, true);
    $scope.$watch('filterOptions', function (newVal, oldVal) {
        if (newVal !== oldVal) {
          $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
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
        columnDefs: [{field: 'id', displayName: '订单ID'},
                     {field:'user_id',displayName:'用户ID'},
                     {field:'pile_id',displayName:'电桩ID'},
                     {field:'ano_book_start',displayName:'订单开始时间'},
                     {field:'ano_book_end',displayName:'订单结束时间'},
                     {field:'electricity',displayName:'电桩电量'},
                     {field:'status', displayName:'订单状态', cellTemplate: '<div ng-class="{green: row.getProperty(col.field) > 30}"><div class="ngCellText">{{row.getProperty(col.field)}}</div></div>'}]
    };
    $scope.seach = function(){
      console.log($scope.start);
      $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    }
   $scope.deleteorder = function(){
          $('#book_ID').val($scope.mySelections[0].id);
          $('#pile_id').val($scope.mySelections[0].pile_id);
          $('#deleteModal').modal('show');

   }

   $scope.deleteor = function(){
    var bookid = $('#book_ID').val();
    var promise = ResTool.httpGetWithToken(pileBookRes.deleteBook,{id:$scope.gridOptions.selectedItems[0].id},{});
    promise.then(function(rc){
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
       $('#deleteModal').modal('hide');
       swal("该订单已经取消", "", "success");
    })
    
   }
}])