'use strict';

angular.module('luna')
  .run(
    ['$rootScope', '$state', '$stateParams', 'ResTool', 'ToasterTool', 'AlertTool', 'AuthTool', 'DialogTool',
      function($rootScope, $state, $stateParams, ResTool, ToasterTool, AlertTool, AuthTool, DialogTool) {
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;
        $rootScope.ResTool = ResTool;
        $rootScope.AlertTool = AlertTool;
        $rootScope.ToasterTool = ToasterTool;
        $rootScope.AuthTool = AuthTool;
        $rootScope.DialogTool = DialogTool;
      }
    ]
  )
  .run(
    function () {
      // 设置全局moment控件的语言
      moment.locale('zh-cn');
    }
  )
  // 自动登录逻辑
  .run(
    ['$state', '$timeout', 'AuthTool', 'ResTool', 'ToasterTool', 'AccountRes', 'WorkspaceRes', function ($state, $timeout, AuthTool, ResTool, ToasterTool, AccountRes, WorkspaceRes) {
      // 常量
      var TOKEN_HEADER = 'x-auth-token';
      // 自动登录系统
      var loginUser = AuthTool.loadLoginInfo();

      if(loginUser && !AuthTool.isLogin()) {
        var promise = ResTool.httpPost(AccountRes.accountAuthentication, null, null, {
          'X-Username': loginUser.username,
          'X-Password': loginUser.password
        });

        promise.then(function success(data) {
          if (data.success) {
            AuthTool.login(data.data, data.headers[TOKEN_HEADER]);

            ResTool.httpGetWithToken(WorkspaceRes.workspaces, null, null)
              .then(function (data) {
                if(data.success) {
                  if(!data.data) data.data = [];

                  AuthTool.updateWorkspaceList(data.data);
                  AuthTool.checkCurrWorkspace();

                  // 获取登录用户在该工作空间/团队的角色和权限信息
                  ResTool.httpGetWithWorkspace(WorkspaceRes.memberRoles, null, null)
                    .then(function (data) {
                      if(data.success) {

                        AuthTool.updateLoginUserRolesAndPermissions(data.data.roles, data.data.permissions);

                        // 跳转到后台首页
                        $timeout(function () {
                          $state.go('app.home');
                        }, 0);
                        ToasterTool.success("欢迎您回来，一起努力工作吧!");

                      }
                    });
                }
              });
          }
        });
      }
    }]
  )
  // 监视需要登录的页面/登录后不能重复登录
  .run(['$state', '$rootScope', '$timeout', 'AuthTool', function ($state, $rootScope, $timeout, AuthTool) {
    $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
      if(toState.access !== undefined) {
        if(toState.access.requiresLogin) {
          if(!AuthTool.isLogin()) {
            $timeout(function () {
              $state.go('portal.login');
            }, 0);
          }
        }
      }

      if(toState.name == 'portal.login') {
        if(AuthTool.isLogin()) {
          $timeout(function () {
            $state.go('app.home');
          }, 0);
        }
      }
    });
  }])
  // 监视不同类型的工作空间(团队)可以访问的页面
  .run(['$state', '$rootScope', '$timeout', 'AuthTool', function ($state, $rootScope, $timeout, AuthTool) {
    $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
      var currWorkspace = AuthTool.getCurrWorkspace();

      if(currWorkspace && currWorkspace.type) {
        if(currWorkspace.type.code == 'TEAM') {
          if(toState.name == 'app.loan-config') {
            $timeout(function () {
              $state.go('app.home');
            }, 0);
          }
        } else if(currWorkspace.type.code == 'PERSONAL') {
          if(toState.name == 'app.team-config' || toState.name == 'app.team-member' || toState.name == 'app.team-apply') {
            $timeout(function () {
              $state.go('app.home');
            }, 0);
          }
        }
      }
    });
  }])
  // 页面切换滚动到页面顶部
  .run(['$rootScope', '$window', function ($rootScope, $window) {
    $rootScope.$on('$stateChangeSuccess', function () {
      $window.scrollTo(0, 0);
    });
  }]);