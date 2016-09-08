app.controller('newpileController', ['$scope','$stateParams','ResTool','SweetAlert','newPileRes', function($scope,$stateParams,ResTool,SweetAlert,newPileRes){
     $scope.pile = {};
    $('#myDatepickerInput1').datepicker();
    $('#myDatepickerInput2').datepicker();
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
        ResTool.httpGetWithToken(newPileRes.getall,{limit:10},{}).then(
          function(rc){
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
        columnDefs: [{field: 'name', displayName: '电桩名称'},
                     {field:'id',displayName:'申请id'},
                     {field:'ident',displayName:'身份证'},
                     {field:'mobile',displayName:'联系电话'},
                     {field:'memo',displayName:'备注'},
                     {field:'owner_id', displayName:'拥有者id', cellTemplate: '<div ng-class="{green: row.getProperty(col.field) > 30}"><div class="ngCellText">{{row.getProperty(col.field)}}</div></div>'}]
    };


  $scope.newpile=function(){
    $('#pileownerid').val($scope.mySelections[0].owner_id);
    $('#pilename').val($scope.mySelections[0].name);
    $('#newpilemodal').modal("show");

  }
  $scope.switchStatus =false;
  $scope.switchStatus1 =false;
  $scope.switchStatus2 =false;
  $scope.pile.last_maintain_time = $("#myDatepickerInput1").val()+" "+"00:00:00";
  $scope.pile.next_maintain_time = $("#myDatepickerInput2").val()+" "+"00:00:00";
 $scope.createpile = function(){
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
     $scope.pile.last_maintain_time = $scope.start+" "+"00:00:00";
  $scope.pile.next_maintain_time = $scope.end+" "+"00:00:00";
    var parametebody = {
        name:$scope.pile.pilename,
        longitude:$scope.pile.pilelongitude,
        latitude:$scope.pile.pilelatitude,
        software_version:$scope.pile.pilesoftware,
        can_book:$scope.switchStatus,
        is_available:$scope.switchStatus1,
        is_qualified:$scope.switchStatus2,
        last_maintain_time:$scope.pile.last_maintain_time,
        next_maintain_time:$scope.pile.next_maintain_time
    }
    console.log(parametebody);

    ResTool.httpPostWithToken(newPileRes.newpile,{},{
        pile_app_id:$scope.mySelections[0].id,
        name:$scope.pile.pilename,
        longitude:$scope.pile.pilelongitude,
        latitude:$scope.pile.pilelatitude,
        software_version:$scope.pile.pilesoftware,
        can_book:$scope.switchStatus,
        is_available:$scope.switchStatus1,
        is_qualified:$scope.switchStatus2,
        last_maintain_time:$scope.pile.last_maintain_time,
        next_maintain_time:$scope.pile.next_maintain_time,
        sn:$scope.pile.sn
    },{}).then(function(rc){
      $('#newpilemodal').modal("hide");
        swal("新电桩创建成功", "", "success");
    });
     $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
 }

}])