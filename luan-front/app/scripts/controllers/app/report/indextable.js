app.controller('indexTableCtrl', ['$scope','$stateParams','ResTool','parameterRes', function($scope,$stateParams,ResTool,parameterRes){

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
        ResTool.httpGetWithToken(parameterRes.getall,{limit:1000},{}).then(
          function(rc){
            
            for(var i =0;i<rc.rows.length;i++){
              if (rc.rows[i].param.communication == 0) {
                rc.rows[i].param.communication = "本地";
              }else if(rc.rows[i].param.communication == 1){
                rc.rows[i].param.communication = "GPRS";
              }else{
                rc.rows[i].param.communication = "WIFI";
              }
              if (rc.rows[i].param.pm25 == 0) {
                rc.rows[i].param.pm25 = "配置";
              }else if (rc.rows[i].param.pm25 == 1){
                rc.rows[i].param.pm25 = "不配置";
              }
              if (rc.rows[i].param.screen == 0) {
                rc.rows[i].param.screen = "配置";
              }else if (rc.rows[i].param.screen == 1){
                rc.rows[i].param.screen = "不配置";
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
        columnDefs: [{field: 'version', displayName: '参数配置版本'},
                     {field:'param.communication',displayName:'通信方式'},
                     {field:'param.pm25',displayName:'PM25配置状态'},
                     {field:'param.screen',displayName:'屏幕配置情况'},
                     {field:'timestamp',displayName:'参数开始修改时间'}]
    };



     
    $scope.chooseupdate = function(){
      $('#updateversion').val($scope.mySelections[0].pile_sn);
      // $('#updatebase').val($scope.mySelections[0].Base);
      // $('#updatehexfile').val($scope.mySelections[0].HEXfileMD5);
      // $('#updatebase64').val($scope.mySelections[0].BinaryBase64MD5);
      $("#updatemodal").modal("show");
    }
    $scope.updateparameter = function(){
      var updatepromise = ResTool.httpGetWithToken(parameterRes.updateparameter,{id:$scope.mySelections[0].id},{});
      updatepromise.then(function(rc){
        console.log(rc);
        $("#updatemodal").modal("hide");
      swal("已提交","","success");
      })
      
    }
    $scope.chooseedit = function(){
      if ($scope.mySelections[0].param.communication =="本地") {
        $("#Communication1").attr("checked","checked");
      }else if ($scope.mySelections[0].param.communication =="GPRS") {
        $("#Communication2").attr("checked","checked");
      }else{
        $("#Communication3").attr("checked","checked");
      }

      if ($scope.mySelections[0].param.pm25 == "配置") {
        $("#pm1").attr("checked","checked");
      }else{
        $("#pm2").attr("checked","checked");
      }
      if ($scope.mySelections[0].param.screen == "配置") {
        $("#screen1").attr("checked","checked");
      }else{
        $("#screen2").attr("checked","checked");
      }
      if ($scope.mySelections[0].param.language == 0) {
        $("#language1").attr("checked","checked");
      }else{
        $("#language2").attr("checked","checked");
      }
      if ($scope.mySelections[0].param.light == "配置") {
        $("#light1").attr("checked","checked");
      }else{
        $("#light2").attr("checked","checked");
      }
      // $('#updateversion').val($scope.mySelections[0].Version);
      // $('#updatebase').val($scope.mySelections[0].Base);
      // $('#updatehexfile').val($scope.mySelections[0].HEXfileMD5);
      // $('#updatebase64').val($scope.mySelections[0].BinaryBase64MD5);
      $('#indexnumber').val($scope.mySelections[0].version);
      $("#pileid").val($scope.mySelections[0].pile_sn);
      $("#myDatepickerInput1").val($scope.mySelections[0].param.devicetime);
      $("#inputPassword3").val($scope.mySelections[0].param.ammeterid);
      $("#input6v").val($scope.mySelections[0].param.cp6);
      $("#input9v").val($scope.mySelections[0].param.cp9);
      $("#input12v").val($scope.mySelections[0].param.cp9);
      $("#voltage").val($scope.mySelections[0].param.voltage);
      $("#current").val($scope.mySelections[0].param.current);
      $("#temperature").val($scope.mySelections[0].param.temperature);
      $("#maxcurrent").val($scope.mySelections[0].param.maxcurrent);
      $("#maxtime").val($scope.mySelections[0].param.maxtime);
      $("#commoneprice").val($scope.mySelections[0].param.commoneprice);
      $("#multistepprice").val($scope.mySelections[0].param.multistepprice);
      $("#price1starttime").val($scope.mySelections[0].param.price1starttime);
      $("#price1endtime").val($scope.mySelections[0].param.price1endtime);
      $("#multistep2price").val($scope.mySelections[0].param.multistep2price);
      $("#price2starttime").val($scope.mySelections[0].param.price2starttime);
      $("#price2endtime").val($scope.mySelections[0].param.price2endtime);
      $("#editmodal").modal("show");
    }
    
    $scope.submitedit = function(){
      var editpromise = ResTool.httpPostWithToken(parameterRes.editparameter,{},{
         id:$scope.mySelections[0].id,
         
      param:{
        communication:$('[name = "Communication"]:checked').val(),
        pm25:$('[name = "pm"]:checked').val(),
        screen:$('[name = "screen"]:checked').val(),
        language:$('[name = "language"]:checked').val(),
        light:$('[name = "light"]:checked').val(),
        devicetime:$("#myDatepickerInput1").val(),
        ammeterid:$("#inputPassword3").val(),
        cp6:$("#input6v").val(),
        cp9:$("#input9v").val(),
        cp12:$("#input12v").val(),
        voltage:$("#voltage").val(),
        current:$("#current").val(),
        temperature:$("#temperature").val(),
        maxcurrent:$("#maxcurrent").val(),
        maxtime:$("#maxtime").val(),
        commoneprice:$("#commoneprice").val(),
        multistepprice:$("#multistepprice").val(),
        price1starttime:$("#price1starttime").val(),
        price1endtime:$("#price1endtime").val(),
        multistep2price:$("#multistep2price").val(),
        price2starttime:$("#price2starttime").val(),
        price2endtime:$("#price2endtime").val()
      }
      },{});
      editpromise.then(function(rc){
        swal("编辑成功","","success");
        $("#editmodal").modal("hide");
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
        console.log(rc);
      })
    }
     $scope.choosedelete = function(){
      $('#deleteupdateversion').val($scope.mySelections[0].pile_sn);

      
      $("#deletemodal").modal("show");
    }
    $scope.deleteparameter = function(){
      var deletepromise = ResTool.httpGetWithToken(parameterRes.deleteparameter,{id:$scope.mySelections[0].id},{});
      deletepromise.then(function(rc){
         $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.filterOptions.filterText);
        $("#deletemodal").modal("hide");
        swal("成功删除", "", "success");
      }) 
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