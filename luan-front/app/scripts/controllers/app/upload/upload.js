app.controller('uploadController', ['$scope','$stateParams','ResTool', function($scope,$stateParams,ResTool){
   $scope.userChart={
            options: {
              chart: {
                type:'column'
              },
            },
            credits:{
                enabled:false,
            },
            title: {
                text: '智慧云充电桩',
                style:{
                    fontWeight:'bold'
                }
            },
            subtitle: {
                text: '大数据分析'
            },
            xAxis: {
                categories:[1,2,3,4,5,6,7,8,9,10,11,12],
               /* plotBands:[{
                from: 8.5,
                to:12.5,
                color:'rgba(68, 170, 213, .2)',
                label: {
                        text: '预测区',
                        verticalAlign: 'top',
                        style: {
                            fontSize: '12px',
                            fontWeight: 600
                        }

                    }
                }]*/
            },
            yAxis: [{
                min: 0,
                title: {
                    text: '活跃用户数量(人数)'
                },
                plotLines:[{
                color:'red',
                dashStyle:'DashDot',
                value:1150,
                width:2,
                label:{
                    text:'',
                    align:'left',
                    x:10,
                     style: {
                            fontSize: '8px',
                            fontWeight: 200
                        }
                }
                }]
            },{
                title: {
                    text: '同比增长率'
                },
                labels: {
                    format: '{value} %',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
            },
            opposite:true
            }],
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                color:'#7CB5EC',
                type: 'spline',
                name: '真实数据',
                data: [180,200,190,165,170,185,150,178,192.162,171,180]

            }]
        };
        $scope.activatePileChart={
            options: {
              chart: {
                type:'column'
              },
            },
            credits:{
                enabled:false,
            },
            title: {
                text: '智慧云充电桩',
                style:{
                    fontWeight:'bold'
                }
            },
            subtitle: {
                text: '大数据分析'
            },
            xAxis: {
                categories:[1,2,3,4,5,6,7,8,9,10,11,12],
               /* plotBands:[{
                from: 8.5,
                to:12.5,
                color:'rgba(68, 170, 213, .2)',
                label: {
                        text: '预测区',
                        verticalAlign: 'top',
                        style: {
                            fontSize: '12px',
                            fontWeight: 600
                        }

                    }
                }]*/
            },
            yAxis: [{
                min: 0,
                title: {
                    text: '活跃电桩数量(个)'
                },
                plotLines:[{
                color:'red',
                dashStyle:'DashDot',
                value:1150,
                width:2,
                label:{
                    text:'',
                    align:'left',
                    x:10,
                     style: {
                            fontSize: '8px',
                            fontWeight: 200
                        }
                }
                }]
            },{
                title: {
                    text: '同比增长率'
                },
                labels: {
                    format: '{value} %',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
            },
            opposite:true
            }],
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                color:'#7CB5EC',
                type: 'spline',
                name: '真实数据',
                data: [180,200,190,165,170,185,150,178,192.162,171,180]

            }]
        };
        $scope.pileChart={
            options: {
              chart: {
                type:'column'
              },
            },
            credits:{
                enabled:false,
            },
            title: {
                text: '智慧云充电桩',
                style:{
                    fontWeight:'bold'
                }
            },
            subtitle: {
                text: '大数据分析'
            },
            xAxis: {
                categories:[1,2,3,4,5,6,7,8,9,10,11,12],
               /* plotBands:[{
                from: 8.5,
                to:12.5,
                color:'rgba(68, 170, 213, .2)',
                label: {
                        text: '预测区',
                        verticalAlign: 'top',
                        style: {
                            fontSize: '12px',
                            fontWeight: 600
                        }

                    }
                }]*/
            },
            yAxis: [{
                min: 0,
                title: {
                    text: '每月电桩数量'
                },
                plotLines:[{
                color:'red',
                dashStyle:'DashDot',
                value:1150,
                width:2,
                label:{
                    text:'',
                    align:'left',
                    x:10,
                     style: {
                            fontSize: '8px',
                            fontWeight: 200
                        }
                }
                }]
            },{
                title: {
                    text: '同比增长率'
                },
                labels: {
                    format: '{value} %',
                    style: {
                        color: Highcharts.getOptions().colors[0]
                    }
            },
            opposite:true
            }],
            tooltip: {
                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [{
                color:'#7CB5EC',
                type: 'column',
                name: '真实数据',
                data: [180,200,190,165,170,185,150,178,192.162,171,180]

            }]
        };
}])