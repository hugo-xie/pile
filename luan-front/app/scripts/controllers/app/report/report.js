'use strict';

app.controller('ReportCtrl', ['$scope','$stateParams','ResTool','locationRes',function($scope, $stateParams,ResTool,locationRes) {

    
   /* var marker = new AMap.Marker('container',{
      center:[121.48,31.22],
      zoom:13,
      clickable:true,
    });*/
  
   /* marker.on('click',function(){
      $scope.showdetail = !$scope.showdetail;
    })*/
   /* marker.setMap(map);
      var markerclick = function(){
      $scope.$apply(function(){
        $scope.showdetail = !$scope.showdetail;
      })
    };*/
    /*AMap.event.addListener(marker, 'click', markerclick);*/
    
    var start = function(){
      var promise = ResTool.httpGetWithToken(locationRes.getTotal,{limit:1000,sn:$("#pileid").val(),owner_id:$("#ownersid").val()},{});
      promise.then(function(rc){
         for(var i =0;i<rc.rows.length;i++){
              if (rc.rows[i].info.pm25 == "-1") {
                rc.rows[i].info.pm25 = "无数据";
              }
            }
      var markers = [];
      var map = new AMap.Map('container');
      var map = new AMap.Map('container',{
        zoom: 10,
        center: [121.48,31.22]
       });
      var scale = new AMap.Scale({
        visible:true
       }),
      toolBar = new AMap.ToolBar({
        visible:true
       });
      map.addControl(scale);
      map.addControl(toolBar);

      $scope.editpile = function(){
        $('#editpilemodal').modal('show');
      };
     
      $scope.deleterelation = function(){
        $('#deletepilerelationmodal').modal('show');
      }
      rc.rows.forEach(function(marker){
        new AMap.Marker({
          map:map,
          position:[marker.longitude,marker.latitude],
          clickable:true,
        }).on('click',function(){
          if ($('#showdetail').hasClass('shadow')) {
            $('#showdetail').removeClass('shadow');
          }else{
            
          }
          $('#piledetail').text(marker.sn);
          $('#ownerid').text(marker.owner_id);
          $('#pm25').text(marker.info.pm25);
        
         /* for(var i=0;i<rc.rows.length;i++){
          markers[i] = new AMap.Marker({
            map:map,
            position:[marker.longitude,marker.latitude],
            clickable:true,
          });
          markers[i].on('click',function(){
          if ($('#showdetail').hasClass('shadow')) {
            $('#showdetail').removeClass('shadow');
          }else{
            $('#showdetail').addClass('shadow');
          }
          $('#piledetail').text(marker.id);
          $('#ownerid').text(marker.owner_id);
          $('#pm25').text(marker.info.pm25);
          
        });
        }*/
        });

      })
     $scope.closedetail = function(){
        $('#showdetail').addClass('shadow');
      }
      
    })
    }
   $(document).ready(start());
    $scope.search = function(){
      start();
      
    }
   /* $scope.seach = function(){
      var promise = ResTool.httpGetWithToken(locationRes.getTotal,{limit:100,pile_id:$("#pileid").val()},{});
    promise.then(function(rc){
      var markers = [];
      var map = new AMap.Map('container');
      var map = new AMap.Map('container',{
        zoom: 10,
        center: [121.48,31.22]
       });
      var scale = new AMap.Scale({
        visible:true
       }),
      toolBar = new AMap.ToolBar({
        visible:true
       });
      map.addControl(scale);
      map.addControl(toolBar);

      $scope.editpile = function(){
        $('#editpilemodal').modal('show');
      };
     
      $scope.deleterelation = function(){
        $('#deletepilerelationmodal').modal('show');
      }
      rc.rows.forEach(function(marker){
        new AMap.Marker({
          map:map,
          position:[marker.longitude,marker.latitude],
          clickable:true,
        }).on('click',function(){
          if ($('#showdetail').hasClass('shadow')) {
            $('#showdetail').removeClass('shadow');
          }else{
            
          }
          $('#piledetail').text(marker.id);
          $('#ownerid').text(marker.owner_id);
          $('#pm25').text(marker.info.pm25);
        
         
        });

      })
     $scope.closedetail = function(){
        $('#showdetail').addClass('shadow');
      }
      
    })
    }*/
}]);