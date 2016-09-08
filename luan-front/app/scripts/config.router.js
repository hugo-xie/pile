'use strict';

angular.module('luna')
  .run(
    ['$rootScope', '$state', '$stateParams',
      function($rootScope, $state, $stateParams) {
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;

        //初始化弹窗
        $('[data-toggle="popover"]').popover();
      }
    ]
  )
  .config(
    ['$stateProvider', '$urlRouterProvider', 'JQ_CONFIG',
      function($stateProvider, $urlRouterProvider, JQ_CONFIG) {
        /*$urlRouterProvider
          .otherwise('/index');*/
        //portal
        $stateProvider
          .state('portal', {
            abstract: true,
            url: '/portal',
            templateUrl: 'tpl/portal/portal.html',
            resolve: {
              css: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'styles/portal.css',
                ]);
              }]
            }
          })
          .state('portal.index', {
            url: '^/index',
            templateUrl: 'tpl/portal/index.html',
            controller: 'IndexController',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/portal/index.js',
                  'scripts/directives/portal/portal-header.js',
                  'scripts/directives/portal/portal-footer.js'
                ]);
              }]
            }
          })
          .state('portal.login', {
            url: '/signin',
            templateUrl: 'tpl/portal/login.html',
            controller: 'LoginController',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/portal/login.js',
                  'scripts/directives/portal/portal-footer.js',
                  'scripts/directives/portal/portal-header.js'
                ]);
              }]
            }
          })
          .state('portal.share',{
            url:'/share',
            templateUrl:'tpl/portal/share.html',
            controller:'shareController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([
                  
                  ])
              }]
            }
          })
          .state('portal.book',{
            url:'/book',
            templateUrl:'tpl/portal/book.html',
            controller:'dateController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([
                  ])
              }]
            }
          })
          .state('portal.pay',{
            url:'/pay',
            templateUrl:'tpl/portal/pay.html',
            controller:'payController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([])
              }]
            }
          })
          //app
          .state('app', {
            abstract: true,
            url: '/app',
            templateUrl: 'tpl/app/app.html',
            controller:'AppCtrl',
            resolve: {
              css: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app.js',
                  'styles/app.css',
                  'ngDialog'
                ]);
              }]
            }
          })
          .state('app.user', {
            url: '^/app/user',
            templateUrl: 'tpl/app/user/user.html',
            controller: 'UserController',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/user/user.js',
                ]);
              }]
            }
          })
          .state('app.book',{
            url:'^/app/book',
            templateUrl:'tpl/app/book/book.html',
            controller: 'BookController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([
                  'scripts/controllers/app/book/book.js',
                  ]);
              }]
            }
          })

          //数据管理
          .state('app.data', {//二级导航栏
            abstract: true,
            url: '/data',
            templateUrl: 'tpl/app/dataMng/datamenu.html',
            controller:'DataCtrl',
            resolve: {
              css: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/dataMng/dataCtrl.js',
                ]);
              }]
            }
          })
          .state('app.index', {
            abstract: true,
            url: '^/app/index',
            templateUrl: 'tpl/app/economy/emenu.html',
            controller: 'AppIndexController',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/app-index.js',
                ]);
              }]
            }
          })

          
/*          .state('app.emenu', {
            abstract: true,
            url: '^/app/emenu',
            templateUrl: 'tpl/app/environment/emenu.html',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/environment/angular-scroll.js',
                ]);
              }]
            }
          })*/
            .state('app.indexconfigure',{
            url:'^/app/indexconfigure',
            templateUrl:'tpl/app/report/indexconfigure.html',
            controller:'indexconfigureController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([
                  'scripts/controllers/app/report/indexconfigure.js',
                  ]);
              }]
            }
          })
          // .state('app.indexedit',{
          //   url:'^/app/indexedit',
          //   templateUrl:'tpl/app/report/indexedit.html',
          //   controller:'indexTableCtrl',
          //   resolve:{
          //     controller:['$ocLazyLoad',function($ocLazyLoad){
          //       return $ocLazyLoad.load([
          //         'scripts/controllers/app/report/indextable.js',
          //         ]);
          //     }]
          //   }
          // })
          .state('app.pile', {
            url: '^/app/pile',
            templateUrl: 'tpl/app/pile/pile.html',
            controller: 'PileController',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/pile/pile.js',
                ]);
              }]
            }
          })
          .state('app.pmenu', {
            abstract: true,
            url: '^/app/pmenu',
            templateUrl: 'tpl/app/population/pmenu.html',
            controller: 'AppPopulationController',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/population/app-population.js',
                ]);
              }]
            }
          })
          .state('app.newpile',{
            url:'^/app/newpile',
            templateUrl:'tpl/app/report/newpile.html',
            controller:'newpileController',
            resolve:{
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                    'scripts/controllers/app/report/newpile.js',
                ]);
              }]
            }
          })
          .state('app.pilelist',{
            url:'^/app/pilelist',
            templateUrl:'tpl/app/report/pilelist.html',
            controller:'pileListController',
            resolve:{
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                    'scripts/controllers/app/report/pilelist.js',
                ]);
              }]
            }
          })
          
          .state('app.pileapplication',{
            url:'^/app/pileapplication',
            templateUrl:'tpl/app/pile/pileapplication.html',
            controller:'pileapplicationController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([
                  'scripts/controllers/app/pile/pileapplication.js',
                  ])
              }]
            }
          })
          .state('app.terminal',{
            url:'^/app/terminal',
            templateUrl:'tpl/app/terminal/terminal.html',
            controller:'terminalController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([
                  'scripts/controllers/app/terminal/terminal.js',
                  'scripts/controllers/app/pile/pileapplication.js',
                  ])
              }]
            }
          })
          .state('app.indextable', {
            url: '^/app/indextable',
            templateUrl: 'tpl/app/report/indextable.html',
            controller: 'indexTableCtrl',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/report/indextable.js',
                 
                ]);
              }]
            }
          })
          .state('app.upload',{
            url:'^/app/upload',
            templateUrl:'tpl/app/upload/upload.html',
            controller:'uploadController',
            resolve:{
              controller:['$ocLazyLoad',function($ocLazyLoad){
                return $ocLazyLoad.load([
                  'scripts/controllers/app/upload/upload.js',
                  ])
              }]
            }
          })
          .state('app.report', {
            url: '^/app/report',
            templateUrl: 'tpl/app/report/report.html',
            controller: 'ReportCtrl',
            resolve: {
              controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/app/report/report.js',
                 
                ]);
              }]
            }
          })
          //population end
          
          .state('app.profile', {
            abstract: true,
            url: '^/app/profile',
            templateUrl: 'tpl/app/profile/profile.html',
            resolve: {
            }
          })
          .state('app.profile.person', {
            url: '^/app/profile/person',
            templateUrl: 'tpl/app/profile/profile-person.html',
            controller:'PersonCtrl',
            resolve: {
               controller: ['$ocLazyLoad', function($ocLazyLoad) {
                return $ocLazyLoad.load([
                  'scripts/controllers/portal/person.js',
                 
                ]);
              }]
            }
          })
          .state('app.profile.password', {
            url: '^/app/profile/password',
            templateUrl: 'tpl/app/profile/profile-password.html',
            resolve: {

            }
          })
          .state('app.message', {
            url: '^/app/message',
            templateUrl: 'tpl/app/message.html',
            resolve: {

            }
          });
          

      }
    ]
  )
  .run(
  );

//定义请求地址，可修改
var base_Url = 'http://localhost:8080';
