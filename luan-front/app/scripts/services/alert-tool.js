/**
 * 统一的 SweetAlert 提示框工具
 *  ~ 如果要扩展，参考 http://t4t5.github.io/sweetalert/
 *
 * 调用方式
 *
 *  通用 alert(single button)
 *  AlertTool.alert(options).then(function() {
 *
 *  });
 *
 *  confirm alert(double button)
 *  AlertTool.confirm(options).then(function(isConfirm) {
 *    if(isConfirm) {
 *      AlertTool.close();
 *    }
 *  });
 */
angular.module('luna')
  .service('AlertTool', ['SweetAlert', '$q', '$window', function (SweetAlert, $q, $window) {
    this.alert = function (options) {
      var deferred = $q.defer();

      options = options || {};
      options.confirmButtonText = options.confirmButtonText || '确定';
      options.cancelButtonText = options.cancelButtonText || '取消';

      SweetAlert.swal(options, function (data) {
        deferred.resolve(data);
      });

      return deferred.promise;
    };

    this.confirm = function (options) {
      var deferred = $q.defer();

      options = options || {};
      options.showCancelButton = true;
      options.closeOnConfirm = false;
      options.confirmButtonText = options.confirmButtonText || '确定';
      options.cancelButtonText = options.cancelButtonText || '取消';

      SweetAlert.swal(options, function (isConfirm) {
        deferred.resolve(isConfirm);
      });

      return deferred.promise;
    };

    this.successAlert = function (options) {
      options.type = options.type ? options.type : 'success';
      return this.alert(options);
    };

    this.warningAlert = function (options) {
      options.type = options.type ? options.type : 'warning';
      return this.alert(options);
    };

    this.infoAlert = function (options) {
      options.type = options.type ? options.type : 'info';
      return this.alert(options);
    };

    this.errorAlert = function (options) {
      options.type = options.type ? options.type : 'error';
      return this.alert(options);
    };

    this.successConfirm = function (options) {
      options.type = options.type ? options.type : 'success';
      return this.confirm(options);
    };

    this.warningConfirm = function (options) {
      options.type = options.type ? options.type : 'warning';
      return this.confirm(options);
    };

    this.infoConfirm = function (options) {
      options.type = options.type ? options.type : 'info';
      return this.confirm(options);
    };

    this.errorConfirm = function (options) {
      options.type = options.type ? options.type : 'error';
      return this.confirm(options);
    };

    this.close = function () {
      $window.swal.close();
    };
  }]);
