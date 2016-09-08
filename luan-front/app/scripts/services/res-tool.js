/**
 * 统一的 Angular Resource 调用工具
 */
angular.module('luna')
  .service('ResTool', ['$sessionStorage', '$q', '$state', 'AuthTool', function ($sessionStorage, $q, $state, AuthTool) {
    var TOKEN_KEY = "X-Auth-Token",
    token="token",
      WORKSPACE_ID = "X-Workspace-Id",
      CURR_WORKSPACE = "Curr-Workspace";

    function successHandler(deferred, value, responseHeaders) {
      var headers = responseHeaders ? responseHeaders() : {};//if called with no arguments returns an object containing all headers. --from angularjs

      value['headers'] = headers;

      // 全局处理错误逻辑
      if(value.code == "502") { //标记
        //需要重新登录
        AuthTool.logout();
        $state.go('portal.login');
      } else {
        deferred.resolve(value);
      }
    }

    function errorHandler(deferred, httpResponse) {
      //TODO: 统一错误处理
      deferred.resolve(httpResponse);
    }

    /**
     * 添加Token到请求头部
     * @param {Object} headers
     * @return {Object}
     */
    function addToken(headers) {
      headers[token] = $sessionStorage[TOKEN_KEY] || null;
      return headers;
    }

    this.setToken = function (token) {
      $sessionStorage[TOKEN_KEY] = token;
    };

    this.getToken = function () {
      return $sessionStorage[TOKEN_KEY] || null;
    };

    /**
     * 添加WorkspaceId到请求头部
     * @param {Object} headers
     * @return {Object}
     */
    function addWorkspaceId(headers) {
      headers[WORKSPACE_ID] = $sessionStorage[CURR_WORKSPACE].id || null;
      return headers;
    }

    /**
     * GET Method
     */
    this.httpGet = function (resource, params, headers) {
      var deferred = $q.defer();

      resource(headers || {}).get(params,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    this.httpGetWithToken = function (resource, params, headers) {
      var deferred = $q.defer();

      resource(addToken(headers || {})).get(params,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    this.httpGetWithWorkspace = function (resource, params, headers) {
      var deferred = $q.defer();

      var _headers = addToken(headers || {});
      _headers = addWorkspaceId(_headers || {});

      resource(_headers).get(params,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    /**
     * POST Method
     */
    this.httpPost = function (resource, params, body, headers) {
      var deferred = $q.defer();

      resource(headers || {}).post(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    this.httpPostWithToken = function (resource, params, body, headers) {
      var deferred = $q.defer();

      resource(addToken(headers || {})).post(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    this.httpPostWithWorkspace = function (resource, params, body, headers) {
      var deferred = $q.defer();

      var _headers = addToken(headers || {});
      _headers = addWorkspaceId(_headers || {});

      resource(_headers).post(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    /**
     * PUT Method
     */
    this.httpPut = function (resource, params, body, headers) {
      var deferred = $q.defer();

      resource(headers || {}).put(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    this.httpPutWithToken = function (resource, params, body, headers) {
      var deferred = $q.defer();

      resource(addToken(headers || {})).put(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    this.httpPutWithWorkspace = function (resource, params, body, headers) {
      var deferred = $q.defer();

      var _headers = addToken(headers || {});
      _headers = addWorkspaceId(_headers || {});

      resource(_headers).put(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    /**
     * DELETE Method
     */
    this.httpDelete = function (resource, params, body, headers) {
      var deferred = $q.defer();

      resource(headers || {}).delete(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

    this.httpDeleteWithToken = function (resource, params, body, headers) {
      var deferred = $q.defer();

      resource(addToken(headers || {})).delete(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };


    this.httpDeleteWithWorkspace = function (resource, params, body, headers) {
      var deferred = $q.defer();

      var _headers = addToken(headers || {});
      _headers = addWorkspaceId(_headers || {});

      resource(_headers).delete(params, body,
        function success(value, responseHeaders) {
          successHandler(deferred, value, responseHeaders);
        },
        function error(httpResponse) {
          errorHandler(deferred, httpResponse);
        });

      return deferred.promise;
    };

  }]);
