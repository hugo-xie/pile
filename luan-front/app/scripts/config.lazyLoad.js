'use strict';

angular.module('luna')
  .constant('JQ_CONFIG', {
    slimScroll: ['../bower_components/slimscroll/jquery.slimscroll.min.js'],
    slider: [
      '../bower_components/bootstrap-slider/bootstrap-slider.js'
    ]
  })
  // oclazyload config
  .config(['$ocLazyLoadProvider', function ($ocLazyLoadProvider) {
    $ocLazyLoadProvider.config({
      modules: [
        {
          name: 'ui.select',
          files: [
            '../bower_components/ui-select/dist/select.min.js',
            '../bower_components/ui-select/dist/select.min.css'
          ]
        },
        {
          name: 'ngDialog',
          files: [
            '../bower_components/ng-dialog/js/ngDialog.js',
            '../bower_components/ng-dialog/css/ngDialog.css',
            '../bower_components/ng-dialog/css/ngDialog-theme-default.css'
          ]
        },
      ]
    });
  }]);
