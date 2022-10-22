$(document).on('click','#charts .js-plotly-plot',function(event){
    var id = $(this).attr('id').slice(5,);
    if (id<=9 && id>=0){
        $.get(base_url+"get_futures_figure/"+id, function(data1, status){
            var trace2 = {
                x: data1.data.Dates,
                y: data1.line,
                yaxis: 'y2',
                mode: 'lines',
                type: 'scatter',
                marker: {
                    size:25,
                    color:'red',
                },
                hovertemplate: '日経先物225'+
                '<br>'+
                '%{y:.2d}',
                name:'',
              };
            var trace1 = {
                type: 'bar',
                x: data1.data.Dates,
                y: data1.data.Diff,
                marker: {
                    color:data1.data.color,
                },
                hovertemplate: '差引き'+
                '<br>'+
                '%{y:.2d}枚',
                name:'',
              };
    
              
            var data = [trace1, trace2 ];
    
            var layout = { 
                xaxis: {
                    tickangle: 60,
                    tickfont: {
                    size: 16,
                    color: 'lightskyblue',
                  }
                },
                yaxis: {
                    name: ' ',
                    tickfont: {
                        size: 18,
                        color: 'lightskyblue'
                    },
                    tickformat: ",d",
                },
                yaxis2: {
                    overlaying: 'y',
                    side: 'right',
                    name: ' ',
                    showgrid: false,
                    showticklabels: false,
                },
                hovermode: 'x',
                showlegend: false,
                hoverlabel: {
                    bordercolor:'white', 
                    font :{
                        size: 20,
                        color: 'white',
                    }
                },
            };
            $("#mgTitle").html(data1.modal_title)
            $("#myModal").modal()
            $('#myModal').on('shown.bs.modal', function (e) {
                Plotly.newPlot('myDiv', data, layout, {displayModeBar: false});
            })
        });   
    }
    else{
        $.get(base_url+"get_options_figure/"+id, function(data1, status){
            var trace1 = {
                x: data1.data.Date,
                y: data1.data.call,
                type: 'bar',
                marker: {
                    // color:'crimson',
                    color:'#636efa',
                },
                name:'買い',
              };
            
            var trace2 = {
                x: data1.data.Date,
                y: data1.data.put,
                type: 'bar',
                marker: {
                    // color:'lightslategrey',
                    color:'#ff5252',
                },
                name:'売り',
              };  
              
            var data = [trace1, trace2];
    
            var layout = {
                barmode: 'relative',
                xaxis: {
                    tickangle: 60,
                    tickfont: {
                        size: 16,
                        color: 'lightskyblue',
                    },
                    // tickformat: ",d",
                },
                yaxis: {
                    tickfont: {
                        size: 18,
                        color: 'lightskyblue'
                    }
                },
                hovermode: 'x',
                showlegend: false,
                hoverlabel: {
                    bordercolor:'white', 
                    font :{
                        size: 20,
                        color: 'white',
    
                    }
                },
            };
            $("#mgTitle").html(data1.modal_title)
            $("#myModal").modal()
            $('#myModal').on('shown.bs.modal', function (e) {
                Plotly.newPlot('myDiv', data, layout, {displayModeBar: false});
            })
        });   
    }
 
})
