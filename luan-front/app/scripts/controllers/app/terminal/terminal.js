app.controller('terminalController', ['$scope','$stateParams','ResTool','terminalRes', function($scope,$stateParams,ResTool,terminalRes){

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
        ResTool.httpGetWithToken(terminalRes.getall,{limit:1000},{}).then(
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
        columnDefs: [{field: 'base', displayName: 'Base'},
                     {field:'binmd5',displayName:'binmd5'},
                     {field:'hexmd5',displayName:'HEXfileMD5'},
                     {field:'version',displayName:'版本'},
                     {field:'upload_time',displayName:'上传时间'},]
    };

     /*$scope.myData = [{Version: "12.34.56.78", Base:"0x8010000",HEXfileMD5:"2b9a8820ac51819c130ae662daa28cff",BinaryBase64MD5:"477fbd7de7ef083ad2668f9b5c7b7730",uploadtime:"2016-06-20 06:19:25" },
                     {Version: "12.34.56.78", Base:"0x8010000",HEXfileMD5:"2b9a8820ac51819c130ae662daa28cff",BinaryBase64MD5:"477fbd7de7ef083ad2668f9b5c7b7730",uploadtime:"2016-06-20 06:19:25" },
                     {Version: "12.34.56.78", Base:"0x8010000",HEXfileMD5:"2b9a8820ac51819c130ae662daa28cff",BinaryBase64MD5:"477fbd7de7ef083ad2668f9b5c7b7730",uploadtime:"2016-06-20 06:19:25" },
                     {Version: "12.34.56.78", Base:"0x8010000",HEXfileMD5:"2b9a8820ac51819c130ae662daa28cff",BinaryBase64MD5:"477fbd7de7ef083ad2668f9b5c7b7730",uploadtime:"2016-06-20 06:19:25" }];
    $scope.mySelections = [];
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
        i18n:'zh-cn'
         };*/

    $scope.refreshlist = function(){
       $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
    }
    $scope.chooseupdate = function(){
      $('#updateversion').val($scope.mySelections[0].version);
      $('#updatebase').val($scope.mySelections[0].base);
      $('#updatehexfile').val($scope.mySelections[0].hexmd5);
      $('#updatebase64').val($scope.mySelections[0].binmd5);
      $("#updatemodal").modal("show");
    }

    $scope.choosedelete = function(){
      $('#deleteversion').val($scope.mySelections[0].version);
     
      $("#deletemodal").modal("show");
    }
    $scope.deleteterminal = function(){
      var promise = ResTool.httpGetWithToken(terminalRes.deleteterminal,{id:$scope.mySelections[0].id},{});
      promise.then(function(rc){
        swal("该固件成功删除","","success");
        $("#deletemodal").modal("hide");
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
        console.log(rc);
      })
    }
    $scope.updateterminal = function(){
      var updatepromise = ResTool.httpGetWithToken(terminalRes.updateterminal,{},{});
      updatepromise.then(function(rc){
        swal("升级成功","","");
        console.log(rc);
        $("#updatemodal").modal("hide");
      })
    }
    $scope.choosedsubmit = function(){
     
      $("#submitmodal").modal("show");
    }
    $scope.test = function(){
     if ($scope.upall) {
    $scope.upid = false;
    $scope.updetail = false;
   }
   }
    $scope.choosedetail = function(){
    if ($scope.updetail) {
      $scope.upall = false;
      $scope.upid = true;
    }else{
      $scope.upid =false;
    }
   }
}])