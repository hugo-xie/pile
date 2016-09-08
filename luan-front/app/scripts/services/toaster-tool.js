/**
 * 统一的 Toaster 提示框服务
 *  ~ 如果要扩展，参考 https://github.com/jirikavi/AngularJS-Toaster
 *
 * 调用方式
 *  ToasterTool.success('title', 'body');
 *  ToasterTool.info('title', 'body');
 *  ToasterTool.warning('title', 'body');
 *  ToasterTool.error('title', 'body');
 */
angular.module('luna')
  .service('ToasterTool', ['toaster', function (toaster) {
    this.success = function (title, body) {
      toaster.pop({
        type: 'success',
        title: title || '',
        body: body || '',
        showCloseButton: false,
        timeout: 2000
      });
    };

    this.info = function (title, body) {
      toaster.pop({
        type: 'info',
        title: title || '',
        body: body || '',
        showCloseButton: false,
        timeout: 2000
      });
    };

    this.warning = function (title, body) {
      toaster.pop({
        type: 'warning',
        title: title || '',
        body: body || '',
        showCloseButton: false,
        timeout: 2000
      });
    };

    this.error = function (title, body) {
      toaster.pop({
        type: 'error',
        title: title || '',
        body: body || '',
        showCloseButton: false,
        timeout: 2000
      });
    };
  }]);
