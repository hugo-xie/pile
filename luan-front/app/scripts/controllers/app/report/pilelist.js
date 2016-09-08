app.controller('pileListController', ['$scope','$stateParams','ResTool','locationRes','pileDeleteRes','SweetAlert','newPileRes',function($scope, $stateParams,ResTool,locationRes,pileDeleteRes,SweetAlert,newPileRes) {
/*
    var promise = ResTool.httpGetWithToken(locationRes.getTotal,{limit:100},{});
    promise.then(function(rc){
 
      
    })*/
    $('#myDatepickerInput1').datepicker();
    $('#myDatepickerInput2').datepicker();
    $('#ui-datepicker-calendar').css("z-index",9999);
    
     $scope.filterOptions = {
        filterText: "",
        useExternalFilter: true
       }; 
       $scope.totalServerItems = 0;
       $scope.pagingOptions = {
        pageSizes: [20, 30, 40],
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
     $scope.getPagedDataAsync = function (pageSize, page) {        
                /*$http.get('jsonFiles/largeLoad.json').success(function (largeLoad) {
                    $scope.setPagingData(largeLoad,page,pageSize);
                }); */
        ResTool.httpGetWithToken(locationRes.getTotal,{limit:1000,sn:$("#pileid").val(),owner_id:$('#ownersid').val()},{}).then(
          function(rc){
            for(var i =0;i<rc.rows.length;i++){
              if (rc.rows[i].is_available == null) {
                rc.rows[i].is_available = "暂无信息";
              }
              else if (rc.rows[i].is_available == false) {
                rc.rows[i].is_available = "不可用";
              }else if (rc.rows[i].is_available == true) {
                rc.rows[i].is_available = "可用";
              }
              if (rc.rows[i].is_qualified == null) {
                rc.rows[i].is_qualified ="暂无信息";
              }
              else if (rc.rows[i].is_qualified == false) {
                rc.rows[i].is_qualified = "不合格";
              }else if (rc.rows[i].is_qualified == true) {
                 rc.rows[i].is_qualified = "合格";
              }
              if (rc.rows[i].last_maintain_time == null) {
                rc.rows[i].last_maintain_time = "暂无信息";
              } 
              if (rc.rows[i].next_maintain_time == null) {
                rc.rows[i].next_maintain_time = "暂无信息";
              }
               if (rc.rows[i].address == null) {
                rc.rows[i].address = "暂无信息";
              }
               if (rc.rows[i].configuration_status == null) {
                rc.rows[i].configuration_status = "暂无信息";
              }
              if (rc.rows[i].configuration_rate == null) {
                rc.rows[i].configuration_rate = "暂无信息";
              }
              if (rc.rows[i].upgrade_status == null) {
                rc.rows[i].upgrade_status = "暂无信息";
              }
              if (rc.rows[i].upgrade_rate == null) {
                rc.rows[i].upgrade_rate = "暂无信息";
              }
               if (rc.rows[i].owner_id == null) {
                rc.rows[i].owner_id = "暂无桩主";
               }
            }
            $scope.setPagingData(rc,page,pageSize);
            console.log(rc.rows);
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
        enableresizeColumns:true,
        i18n:'zh-cn',
        columnDefs: [{field: 'name', displayName: '电桩名称'},
                     {field:'sn',displayName:'电桩id'},
                     // {field:'longitude',displayName:'电桩经度'},
                     // {field:'latitude',displayName:'电桩纬度'},
                     {field:'owner_id',displayName:'桩主id'},
                     {field:'is_available',displayName:'是否可用'},
                     {field:'is_qualified',displayName:'是否合格'},
                     {field:'last_maintain_time',displayName:'上次维护时间'},
                     {field:'next_maintain_time',displayName:'下次维护时间'},
                     {field:'upgrade_status',displayName:'升级状态'},
                     {field:'upgrade_rate',displayName:'升级进度'},
                     {field:'configuration_status',displayName:'配置状态'},
                     {field:'configuration_rate',displayName:'配置进度'},
                     {field:'electricity', displayName:'电桩电量', cellTemplate: '<div ng-class="{green: row.getProperty(col.field) > 30}"><div class="ngCellText">{{row.getProperty(col.field)}}</div></div>'}]
    };

$scope.pileopen = function(){
    $('#pilename').html($scope.mySelections[0].name);
    $('#pileaddress').html($scope.mySelections[0].address);
    $('#pileopenmodal').modal("show");
  }
  $scope.startpile = function(){
    var pileopenpromise=ResTool.httpPostWithToken(pileDeleteRes.openpile,{},{
      sn:$scope.mySelections[0].sn,
      "open_time":$("#select1 option:selected").text()+":"+$("#select2 option:selected").text()+":00",
      "close_time":$("#select3 option:selected").text()+":"+$("#select4 option:selected").text()+":00"
    });
    pileopenpromise.then(function(rc){
      swal("开放时间设置成功", "", "success");
    });
    $('#pileopenmodal').modal("hide");

  }
  $scope.deleteRelation = function(){
    $("#delepileid").val($scope.mySelections[0].sn);
    $('#deletepilerelationmodal').modal("show");
  }
  $scope.editpile = function(){
    if ($scope.mySelections[0].is_charging == "暂无信息") {
      $scope.mySelections[0].is_charging = false;
    }
    if ($scope.mySelections[0].is_available == "暂无信息") {
      $scope.mySelections[0].is_available = false;
    }else if ($scope.mySelections[0].is_available == "可用") {
      $scope.switchStatus1 = true;
    }else if ($scope.mySelections[0].is_available == "不可用") {
      $scope.switchStatus1 = false;
    }
    if ($scope.mySelections[0].is_qualified == "暂无信息") {
      $scope.switchStatus2 = false;
    }else if ($scope.mySelections[0].is_qualified == "合格") {
      $scope.switchStatus2 = true;
    }else if ($scope.mySelections[0].is_qualified == "不合格"){
      $scope.switchStatus2 = false;
    }
    $('#epileid').val($scope.mySelections[0].sn);
    $('#epilename').val($scope.mySelections[0].name);
    $('#epilerid').val($scope.mySelections[0].owner_id);
    $('#epileaddress').val($scope.mySelections[0].address);
    $('#epilelongi').val($scope.mySelections[0].longitude);
    $('#epilelati').val($scope.mySelections[0].latitude);
    $('#myDatepickerInput1').val($scope.mySelections[0].last_maintain_time);
    $('#myDatepickerInput2').val($scope.mySelections[0].next_maintain_time);
    $scope.switchStatus = $scope.mySelections[0].is_charging;
    // $scope.switchStatus1 = $scope.mySelections[0].is_available;
    // $scope.switchStatus2 = $scope.mySelections[0].is_qualified;
    $('#editpilemodal').modal("show");
  }
  $scope.submitedit = function(){
    if ($('#myDatepickerInput1').val() == "") {
      $scope.start = null;
     }else if ($('#myDatepickerInput1').val().split(" ").length == 2) {
      $scope.start = $('#myDatepickerInput1').val();
     }else{
       $scope.start = moment($('#myDatepickerInput1').val(),"MM-DD-YYYY").format("YYYY-MM-DD");
     }
     if ($('#myDatepickerInput2').val() == "") {
      $scope.end = null;
     }else if ($('#myDatepickerInput2').val().split(" ").length == 2) {
       $scope.start = $('#myDatepickerInput1').val();
     }else{
       $scope.end = moment($('#myDatepickerInput2').val(),"MM-DD-YYYY").format("YYYY-MM-DD");
     }
     var last_maintain_time = $scope.start+" "+"00:00:00";
     var next_maintain_time = $scope.end+" "+"00:00:00";
     if ($('#epileaddress').val() == "暂无信息") {
      $scope.address = "";
     }else{
      $scope.address = $('#epileaddress').val();
     }
     if ($scope.switchStatus1 == "暂无信息") {
      $scope.availeable = "";
     }
     var parameter = {
      id:$scope.mySelections[0].sn,
      name:$('#epilename').val(),
      longitude:$('#epilelongi').val(),
      latitude:$('#epilelati').val(),
      address:$scope.address,
      is_qualified:$scope.switchStatus2,
      is_available:$scope.switchStatus1,
      is_charging:$scope.switchStatus,
      last_maintain_time:last_maintain_time,
      next_maintain_time:next_maintain_time,
      owner_id:$('#epilerid').val()};
      console.log(parameter);
      console.log($('#myDatepickerInput1').val().split(" ").length);
    ResTool.httpPostWithToken(newPileRes.editpile,{id:$scope.mySelections[0].sn},{
      name:$('#epilename').val(),
      longitude:$('#epilelongi').val(),
      latitude:$('#epilelati').val(),
      address:$('#epileaddress').val(),
      is_qualified:$scope.switchStatus2,
      is_available:$scope.switchStatus1,
      is_charging:$scope.switchStatus,
      last_maintain_time:last_maintain_time,
      next_maintain_time:next_maintain_time,
      owner_id:$('#epilerid').val()
    },{}).then(function(rc){
      $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
      $('#editpilemodal').modal("hide");
      swal("编辑成功","","success");
      console.log(rc);
    },function(err){
       swal("该电桩已删除", "", "error");
    })
  }
  $scope.falsenumber = 1;
  $scope.testlongitude = function(){
   var testvalue=$('#epilelongi').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expend = true;
    $scope.falsenumber = 0;
   }else{
    $scope.expend = false;
    $scope.falsenumber = 1;
   }
  }

  $scope.testlatitude = function(){
    var testvalue=$('#epilelati').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expendlatitude = true;
    $scope.falsenumber = 0;
   }else{
    $scope.expendlatitude = false;
    $scope.falsenumber = 1;
   }
  }

  $scope.testid = function(){
    var testvalue=$('#epilerid').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expendid = true;
    $scope.falsenumber = 0;
   }else{
    $scope.expendid = false;
    $scope.falsenumber = 1;
   }
  }
      /*  var promise = ResTool.httpGetWithToken(roleRes.getall,{limit:$scope.pagingOptions.pageSize},{});
        promise.then(function(rc){
          console.log(rc);
        })*/
     $scope.seachuser = function(){
      $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    }
         
   $scope.deletePile = function(){
    ResTool.httpGetWithToken(pileDeleteRes.deletepile,{id:$("#delepileid").val()},{}).then(
      function(rc){
        $('#deletepilerelationmodal').modal("hide");
         swal("该电桩已删除", "", "success");
          $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
      }
      )
   }

   $scope.search = function(){
       $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    }
}]);