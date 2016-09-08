app.controller('indexconfigureController', ['$scope','$stateParams','ResTool','SweetAlert','parameterRes', function($scope,$stateParams,ResTool,SweetAlert,parameterRes){
     $scope.falsenumber = 0;
     $('#myDatepickerInput1').datepicker();
    $('#myDatepickerInput2').datepicker();
    $("#price1starttime").datepicker();
    $("#price1endtime").datepicker();
    $("#price2starttime").datepicker();
    $("#price2endtime").datepicker();
    var mydate = new Date();
    var i;
    $("#indexnumber").val(mydate.getFullYear()+mydate.getMonth()+mydate.getDate());
    var innumber= mydate.getFullYear()+""+mydate.getMonth()+""+mydate.getDate();
    var versionpromise = ResTool.httpGetWithToken(parameterRes.getversion,{},{});
    versionpromise.then(function(rc){
      $scope.indexnumber = rc.version;
      console.log(rc.version);
    })
    
     $scope.testpileid = function(){
    var testvalue=$('#pileid').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expendid = true;
    $scope.falsenumber = 0;
   }else{
    $scope.expendid = false;
    $scope.falsenumber = 1;
   }
  }
  $scope.testeid = function(){
    var testvalue=$('#pileid').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expendeid = true;
    
   }else{
    $scope.expendid = false;
    
   }
  }
  $scope.test6v = function(){
    var testvalue=$('#input6v').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expende6v = true;
    
   }else{
    $scope.expende6v = false;
    
   }
  }
   $scope.test9v = function(){
    var testvalue=$('#input9v').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expende9v = true;
    
   }else{
    $scope.expende9v = false;
    
   }
  }
   $scope.test12v = function(){
    var testvalue=$('#input12v').val();
   var reg = new RegExp("^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|([0-9]*[1-9][0-9]*))$"); 
   if(!reg.test(testvalue)){
    $scope.expende12v = true;
    
   }else{
    $scope.expende12v = false;
    
   }
  }
   
  $scope.submitparameter = function(){
    var body ={
       id:$('#pileid').val(),
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
    };
    console.log(body);
    var submitpromise = ResTool.httpPostWithToken(parameterRes.newparameter,{},{
      pile_sn:$('#pileid').val(),
      version:$('#indexnumber').val(),
      param:{
        indexnumber:$("#indexnumber").val(),
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
    submitpromise.then(function(rc){
      swal("参数配置提交成功","可返回参数配置列表查看","success");
      console.log(rc);
      console.log(i);
    })
  }
}])