function create_chart(result,chart_type){

    var title = result['data']['title'];
    var dates = result['data']['dates'];
    var diff = result['data']['diff'];
    var colors = result['data']['colors'];
    var line = result['data']['line'];

    if (chart_type == "archive"){
        var dates_between = result['data']['graph_between'];
    }
    else{
        var dates_between = null;
    }

    const data = {
        labels: dates,
        datasets: [{
            type: 'bar',
            label: 'Bar graph',
            xAxisID: 'x-axis-bar',
            data: diff,
            borderColor: colors,
            backgroundColor: colors,
            borderWidth: 2,
            pointRadius: 5,
            pointBorderWidth: 1,
            pointHoverRadius: 7,
            pointHoverBorderWidth: 2,
            showLabelBackdrop:true,
            fill: true,
            order:2
        }, {
            order:1,
            type: 'line',
            label: 'Line graph',
            yAxisID: 'y-axis-line',
            xAxisID: 'x-axis-line',
            data: line,
            fill: false,
            borderColor: '#ff5252',
            backgroundColor: '#ff5252',
            lineTension: 0.5,
            borderCapStyle: 'butt',
            borderDash: [],
            borderDashOffset: 0.0,
            borderJoinStyle: 'miter',
            pointBorderWidth: 1,
            pointHoverRadius: 6,
            pointRadius: 3,
            pointHitRadius: 10,
        }]
    };
    const config = {
        data: data,
        options: {
            interaction:{
                mode:'index'
            },
            layout: {
                padding: 20
            },
            responsive: true,
            scales: {
                y: {
                    display:false,
                },
                'x-axis-bar':{
                    ticks:{
                        autoSkip:false,
                        font: {
                            size: 16
                        },
                        color: "#ffffff",
                    }
                },
                'x-axis-line':{
                  display:false  
                }
            },
            plugins: {
                legend:{
                    display:false
                },
                tooltip:{
                    // displayColors:false,
                    backgroundColor: function (context){
                        if (context.tooltip.dataPoints[0].dataset.type === 'line'){
                            return '#c93a32'
                        }
                        if (context.tooltip.dataPoints[0].raw.y < 0){
                            return '#ff8a8a'
                        }
                        return '#636efa'
                    },
                    borderColor: function (context){
                        return '#fefefe'
                    },
                    bodyFont:{
                        size:20
                    },
                    titleFont:{
                        size:20
                    },
                    titleAlign:'left',
                    bodyAlign:'left',
                    callbacks:{
                        beforeTitle: function (context){
                            if(context[0].dataset.type==='bar'){
                                return '差し引き'
                            }
                            if (context[0].dataset.type==='line' && context[0].chart.id < 6 || context[0].chart.id > 9){
                                return '日経225先物'
                            }
                            else{
                                return 'TOPIX先物'
                            }
                        },
                        label: function (context){
                            if (context.dataset.type!=='line'){
                                return context.parsed.y+" 枚"
                            }
                            else{
                                return context.parsed.y
                            }
                        }
                    },
                },
                title: {
                    display: true,
                    text: dates_between?title+dates_between:title,
                    padding: {
                        top: 20,
                    },
                    font: {
                        size: 22,
                    },
                    color: "#ffffff"
                },
            }
        }
    };

    return config
}