/**
 * 统一的权限控制工具
 *
 */
angular.module('luna')
  .service('AuthTool', ['$localStorage', '$sessionStorage', function ($localStorage, $sessionStorage) {

    //常量
    var TOKEN_KEY = 'X-Auth-Token',
      LOGIN_USER = 'Login-User',
      CURR_WORKSPACE = 'Curr-Workspace',
      WORKSPACE_LIST = 'Workspace-List',
      USERNAME = 'username',
      PASSWORD = 'password',
      USER_EMAIL = 'useremail',
      USER_ACCOUNT = 'useraccount',
      USER_ROLE = 'userrole';

    this.isLogin = function () {
      return $sessionStorage[LOGIN_USER] && $sessionStorage[TOKEN_KEY];
    };

    this.login = function (user, token,username,useremail,useraccount,userrole) {
      $sessionStorage[LOGIN_USER] = user;
      $sessionStorage[TOKEN_KEY] = token;
      $sessionStorage[USERNAME] = username;
      $sessionStorage[USER_EMAIL] = useremail;
      $sessionStorage[USER_ACCOUNT] = useraccount;
      $sessionStorage[USER_ROLE] = userrole;
    };

    this.logout = function () {
      var loginUser = this.getLoginUser();

      delete $sessionStorage[CURR_WORKSPACE];
      delete $sessionStorage[WORKSPACE_LIST];

      if(loginUser && loginUser.id)
        delete $localStorage[CURR_WORKSPACE + loginUser.id];

      delete $sessionStorage[LOGIN_USER];
      delete $sessionStorage[TOKEN_KEY];

      delete $localStorage[USERNAME];
      delete $localStorage[PASSWORD];
    };

    this.getLoginUser = function () {
      return $sessionStorage[LOGIN_USER];
    };

    this.updateLoginUser = function (user) {
      $sessionStorage[LOGIN_USER] = user;
    };

    this.updateLoginUserRolesAndPermissions = function (roles, permissions) {
      $sessionStorage[LOGIN_USER].roles = roles;
      $sessionStorage[LOGIN_USER].permissions = {};
      angular.forEach(permissions, function (item) {
        $sessionStorage[LOGIN_USER].permissions[item.code] = item.value;
      });
    };

    this.saveLoginInfo = function (username, password) {
      $localStorage[USERNAME] = username;
      $localStorage[PASSWORD] = password;
    };

    this.saveWorkspaceInfo = function (workspace) {
      var loginUser = this.getLoginUser();
      $localStorage[CURR_WORKSPACE + loginUser.id] = workspace;
    };

    this.getCurrWorkspace = function () {
      return $sessionStorage[CURR_WORKSPACE];
    };

    //--临时方法
    this.setCurrWorkspace = function (workspace) {
      $sessionStorage[CURR_WORKSPACE] = workspace;
    };
    //--临时方法

    this.updateCurrWorkspace = function (workspace) {
      $sessionStorage[CURR_WORKSPACE] = workspace;

      var list = this.getWorkspaceList();
      for(var i = 0; i < list.length; i++) {
        if(list[i].id == workspace.id) {
          list[i] = workspace;
          break;
        }
      }
    };

    this.checkCurrWorkspace = function () {
      var workspaceList = this.getWorkspaceList();
      /**
       * 检查localstorage是否保存最近访问团队的记录,
       * 存在则设置当前团队为最近访问团队, 不存在则设置当前团队为列表第一个团队
       */

      var historyWorkspace = this.loadWorkspaceInfo();
      if(historyWorkspace && historyWorkspace.id) {
        var i, len;
        for(i = 0, len = workspaceList.length; i < len; i++) {
          if(historyWorkspace.id == workspaceList[i].id) {
            this.updateCurrWorkspace(workspaceList[i]);
          }
        }

        if(!this.getCurrWorkspace()) {
          this.updateCurrWorkspace(workspaceList[0]);
          this.saveWorkspaceInfo(workspaceList[0]);
        }
      } else {
        this.updateCurrWorkspace(workspaceList[0]);
        this.saveWorkspaceInfo(workspaceList[0]);
      }
    };

    // 删除当前所在团队
    this.deleteCurrWorkspace = function () {
      var currWorkspace = this.getCurrWorkspace(),
        workspaceList = this.getWorkspaceList();

      var i, len;
      for(i = 0, len = workspaceList.length; i < len; i++) {
        if(currWorkspace.id == workspaceList[i].id) {
          workspaceList.splice(i, 1);
          break;
        }
      }

      this.updateWorkspaceList(workspaceList);
    };

    // 跳转到个人贷款空间
    this.jumpPersonalWorkspace = function () {
      var i, len, workspaceList = this.getWorkspaceList();

      // 跳转到个人贷款空间
      var personWorkspace = null;
      for(i = 0, len = workspaceList.length; i < len; i++) {
        if(workspaceList[i].isDefault || workspaceList[i].type.code == 'PERSONAL') {
          personWorkspace = workspaceList[i];
        }
      }
      if(!personWorkspace) {
        personWorkspace = workspaceList[0];
      }
      this.updateCurrWorkspace(personWorkspace);
      this.saveWorkspaceInfo(personWorkspace);
    };

    this.getWorkspaceList = function () {
      return $sessionStorage[WORKSPACE_LIST];
    };

    this.updateWorkspaceList = function (workspaceList) {
      $sessionStorage[WORKSPACE_LIST] = workspaceList;
    };

    this.loadLoginInfo = function () {
      if ($localStorage[USERNAME] && $localStorage[PASSWORD]) {
        return {
          username: $localStorage[USERNAME],
          password: $localStorage[PASSWORD]
        };
      } else {
        return null;
      }
    };

    this.loadWorkspaceInfo = function () {
      var loginUser = this.getLoginUser();
      return $localStorage[CURR_WORKSPACE + loginUser.id];
    };

    // 密码加密函数
    this.encryptPassword = function (password, username, sbin) {
      var code = sbin === undefined ? '1234' : sbin;

      return md5(md5(md5(password) + username) + code.toUpperCase());
    };
  }]);
