app.controller('PersonCtrl', ['$scope', '$rootScope', '$state', 'ResTool','$sessionStorage',  
  function($scope, $rootScope, $state, ResTool,$sessionStorage ) {
  // 登录用户结构
  var TOKEN_KEY = 'X-Auth-Token',
      LOGIN_USER = 'Login-User',
      CURR_WORKSPACE = 'Curr-Workspace',
      WORKSPACE_LIST = 'Workspace-List',
      USERNAME = 'username',
      PASSWORD = 'password',
      USER_EMAIL = 'useremail',
      USER_ACCOUNT = 'useraccount',
      USER_ROLE = 'userrole';
      $scope.contact = {};
     $("#username").val($sessionStorage[USERNAME]);
     $scope.contact.name = $sessionStorage[USERNAME];
     $scope.contact.email = $sessionStorage[USER_EMAIL];
     $scope.contact.account = $sessionStorage[USER_ACCOUNT];
     if ($sessionStorage[USER_ROLE] == "admin") {
      $("#userrole").val("您为管理员用户，具有最高权限");
     }else if ($sessionStorage[USER_ROLE] == "user") {
      $("#userrole").val("您为普通用户，具有最低权限");
     }else if ($sessionStorage[USER_ROLE] == "merchant") {
      $("#userrole").val("您为商家用户，具有普通权限");
     }
     console.log($sessionStorage[USER_ROLE]);

}]);
