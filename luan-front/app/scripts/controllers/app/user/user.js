app.controller('UserController', ['$scope','$stateParams','ResTool','SweetAlert','roleRes', function($scope,$stateParams,ResTool,SweetAlert,roleRes){
  /*$scope.myData = [{name: "Moroni", age: 50},
                    {name: "Tiancum", age: 43},
                    {name: "Jacob", age: 27},
                    {name: "Nephi", age: 29},
                    {name: "Enos", age: 34}];
    $scope.gridOptions = { 
        data: 'myData',
        columnDefs: [{field: 'name', displayName: 'Name'},
                     {field:'age', displayName:'Age', cellTemplate: '<div ng-class="{green: row.getProperty(col.field) > 30}"><div class="ngCellText">{{row.getProperty(col.field)}}</div></div>'}]
        };*/
        $scope.switchStatus=false;
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
        ResTool.httpGetWithToken(roleRes.getall,{limit:1000,mobile:$scope.pillermobile,plate:$scope.pilerplate,onlyOwner:$scope.switchStatus},{}).then(
          function(rc){
            for(var i =0;i<rc.rows.length;i++){
              if (rc.rows[i].can_login == true) {
                rc.rows[i].can_login = "可以登录";
              }else{
                rc.rows[i].can_login = "不可以登录";
              }
              if (rc.rows[i].role == "user") {
                rc.rows[i].role = "用户";
              }else if (rc.rows[i].role == "merchant"){
                rc.rows[i].role = "商家";
              }else if (rc.rows[i].role == "admin") {
                rc.rows[i].role = "管理员";
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
        i18n:'zh-cn',
        columnDefs: [{field: 'name', displayName: '用户名'},
                     {field:'nick',displayName:'昵称'},
                     {field:'role',displayName:'角色'},
                     {field:'mobile',displayName:'联系电话'},
                     {field:'plate',displayName:'用户车牌'},
                     {field:'can_login',displayName:'是否可以登录'},
                     {field:'account_credits',displayName:'用户积分'},
                     {field:'email', displayName:'电子邮件', cellTemplate: '<div ng-class="{green: row.getProperty(col.field) > 30}"><div class="ngCellText">{{row.getProperty(col.field)}}</div></div>'}]
    };


      /*  var promise = ResTool.httpGetWithToken(roleRes.getall,{limit:$scope.pagingOptions.pageSize},{});
        promise.then(function(rc){
          console.log(rc);
        })*/

     $scope.seachuser = function(){
      console.log($scope.switchStatus);
      $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    }
         $scope.uprole= function(){
          $('#userrolename').val($scope.gridOptions.selectedItems[0].name);
          
            $('#currentrole').val($scope.gridOptions.selectedItems[0].can_login);
         
          
          $('#deleteModal').modal('show');
    }
    $scope.downrole= function(){
          $('#downuserrolename').val($scope.gridOptions.selectedItems[0].name);
          if ($scope.gridOptions.selectedItems[0].can_login =="可以登录") {
            $('#downcurrentrole').val("可以登录");
          }else{
            $('#downcurrentrole').val("不能登录");
          };
          $('#downModal').modal('show');
    }
     $scope.addnewuser= function(){
      var parameter = {
            name:$('#addusername').val(),
            nick:$('#addusernickname').val(),
            role:$('#roleselect option:selected').text(),
            can_login:true,
            email:$('#adduseremail').val(),
            mobile:$('#adduserphone').val(),
            plate:$('#adduserplate').val()
          };
          if ($("#loginselect option:selected").text() == true) {
              parameter.can_login = true;
          }else{
            parameter.can_login = false;
          }
          
          console.log(parameter);
          var promise = ResTool.httpPostWithToken(roleRes.adduser,{},{
            name:$('#addusername').val(),
            nick:$('#addusernickname').val(),
            role:$('#roleselect option:selected').text(),
            can_login:false,
            email:$('#adduseremail').val(),
            mobile:$('#adduserphone').val(),
            plate:$('#adduserplate').val()
          },{});
          promise.then(function(rc){
            console.log(rc);
            swal("增加成功","","success");
          });
           $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
          $('#addModal').modal('hide');
    }
    $scope.adduser= function(){
          
         
          $('#addModal').modal('show');
    }
   $scope.upcurrentrole = function(){
    $('#deleteModal').modal('hide');
    if ($('#currentrole').val() == "可以登录") {
      swal("已经是最高权限", "", "error");
    }else{
      var userid = $('#userrolename').val();
      var promise = ResTool.httpGetWithToken(roleRes.uprole,{id:$scope.gridOptions.selectedItems[0].id},{});
      $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
      promise.then(function(rc){
        swal("该用户权限提升成功", "", "success");
      });
      
    }
    
   }
    $scope.downcurrentrole = function(){
    $('#downModal').modal('hide');
    if ($('#downcurrentrole').val() == "不能登录") {
      swal("已经是最低权限", "", "error");
    }else{
      var userid = $('#userrolename').val();
      var promise = ResTool.httpGetWithToken(roleRes.downrole,{id:$scope.gridOptions.selectedItems[0].id},{});
     
      promise.then(function(rc){
         $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
        swal("该用户权限降低成功", "", "success");
      });
      
    }
    
   }

}])