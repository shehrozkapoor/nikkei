function myFunction(para) {
    document.getElementById("charts").innerHTML = "";
    const array = []
    for (let key in para) {
        var newdiv = document.createElement("div");
        newdiv.setAttribute("id", `${key}`);
        document.body.appendChild(newdiv);

        var element = document.getElementById("charts");
        element.appendChild(newdiv);
        var trace2 = {
            x: para[key].data.Dates,
            y: para[key].chart_line,
            yaxis: 'y2',
            type: 'scatter',
            marker: {
                size: 25,
                color: 'red',
            },
            hovertemplate: '日経先物225' +
                '<br>' +
                '%{y:.2d}',
            name: '',
        };
        var trace1 = {
            type: 'bar',
            x: para[key].data.Dates,
            y: para[key].data.Diff,
            marker: {
                color: para[key].data.color,
            },
            hovertemplate: '差引き' +
                '<br>' +
                '%{y:.2d}枚',
            name: '',
        };


        var data = [trace1, trace2];

        var layout = {
            title: {
                text: para[key].chart_title,
                font: {
                    color: '#76caee',
                    textshadow: '#2cb8f5',
                    size: 16,
                },
                xref: 'paper',
                x: 0,
            },
            width: 650,
            height: 400,
            margin: {
                l: 90,
                r: 50,
                b: 100,
                t: 70,
                pad: 4
            },
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
                bordercolor: 'white',
                font: {
                    size: 20,
                    color: 'white',
                }
            },
        };
        array.push(Plotly.newPlot(`${key}`, data, layout, {
            displayModeBar: false
        }));
    }
    for (let i in array) {
        chart_function(i)
    }
}

function chart_function(event, para1) {
    return para1
}

function myFunc(parameter) {
    document.getElementById("charts").innerHTML = "";
    const arr = [];
    for (let key in parameter) {
        var newdiv = document.createElement("div");
        newdiv.setAttribute("id", `${key}`);
        document.body.appendChild(newdiv);

        var element = document.getElementById("charts");
        element.appendChild(newdiv);
        var trace1 = {
            x: parameter[key].data.Date,
            y: parameter[key].data.put,
            type: 'bar',
            marker: {
                color: '#ff5252',
            },
            name: '売り',
        };

        var trace2 = {
            x: parameter[key].data.Date,
            y: parameter[key].data.call,
            type: 'bar',
            marker: {
                color: '#636efa',
            },
            name: '買い',
        };

        var data = [trace1, trace2];

        var layout = {
            title: {
                text: parameter[key].modal_title,

                font: {
                    color: '#76caee',
                    textshadow: '#2cb8f5',
                    size: 16,
                },
                xref: 'paper',
                x: 0,
            },
            width: 650,
            height: 400,
            margin: {
                l: 90,
                r: 50,
                b: 100,
                t: 70,
                pad: 4
            },
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
                bordercolor: 'white',
                font: {
                    size: 20,
                    color: 'white',

                }
            },
        };
        arr.push(Plotly.newPlot(`${key}`, data, layout, {
            displayModeBar: false
        }));
    }
    for (let i in arr) {
        chart_func(i)
    }
}

function chart_func(event, para1) {
    return para1
}

function Func1(arg1, id) {
    for (let key in arg1) {
        for (let key1 in arg1[key]) {
            if (key1 == id) {
                for (let key2 in arg1[key][key1]) {
                    var trace2 = {
                        x: arg1[key][key1].data.Dates,
                        y: arg1[key][key1].chart_line,
                        yaxis: 'y2',
                        type: 'scatter',
                        marker: {
                            size: 25,
                            color: 'red',
                        },
                        hovertemplate: '日経先物225' +
                            '<br>' +
                            '%{y:.2d}',
                        name: '',
                    };
                    var trace1 = {
                        type: 'bar',
                        x: arg1[key][key1].data.Dates,
                        y: arg1[key][key1].data.Diff,
                        marker: {
                            color: arg1[key][key1].data.color,
                        },
                        hovertemplate: '差引き' +
                            '<br>' +
                            '%{y:.2d}枚',
                        name: '',
                    };

                    var data = [trace1, trace2];

                    var layout = {
                        title: {
                            // text: arg1[key][key1].chart_title,
                            font: {
                                color: '#76caee',
                                textshadow: '#2cb8f5',
                                size: 16,
                            },
                            xref: 'paper',
                            x: 0,
                        },
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
                            bordercolor: 'white',
                            font: {
                                size: 20,
                                color: 'white',
                            }
                        },
                    };
                    $("#mgTitle").html(arg1[key][key1].chart_title)
                    $("#archiveModal").modal()
                    $('#archiveModal').on('shown.bs.modal', function (e) {
                        Plotly.newPlot('archiveGraph', data, layout, {
                            displayModeBar: false
                        });
                    });
                }
            }
        }
    }
}

function Func2(arg2, id) {
    fetched_data = arg2['charts_options'][id]
    var trace1 = {
        x: fetched_data.data.Date,
        y: fetched_data.data.put,
        type: 'bar',
        marker: {
            color: '#ff5252',
        },
        name: '売り',
    };

    var trace2 = {
        x: fetched_data.data.Date,
        y: fetched_data.data.call,
        type: 'bar',
        marker: {
            color: '#636efa',
        },
        name: '買い',
    };

    var data = [trace1, trace2];

    var layout = {
        title: {
            // text: fetched_data.modal_title,
            font: {
                color: '#76caee',
                textshadow: '#2cb8f5',
                size: 16,
            },
            xref: 'paper',
            x: 0,
        },
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
            bordercolor: 'white',
            font: {
                size: 20,
                color: 'white',

            }
        },
    };
    $("#mgTitle").html(fetched_data.modal_title)
    $("#archiveModal").modal()
    $('#archiveModal').on('shown.bs.modal', function (e) {
        Plotly.newPlot('archiveGraph', data, layout, {
            displayModeBar: false
        });
    })


}

var main_id = 0
$(document).ready(function (event) {
    // $.get("http://127.0.0.1:8000/eachchart/0", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/0", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});

$(document).on('click', '.each_chart0', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/0", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/0", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart1', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/1", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/1", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart2', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/2", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/2", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart3', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/3", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/3", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart4', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/4", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/4", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart5', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/5", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/5", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart6', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/6", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/6", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart7', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/7", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/7", function (data1, status) {
        for (let key in data1) {
            for (let row in data1[key]) {
                myFunction(data1[key]);
            }
        }
    })
});
$(document).on('click', '.each_chart8', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/8", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/8", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart9', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart/9", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart/9", function (data1, status) {
        for (let key in data1) {
            myFunction(data1[key]);
        }
    })
});

$(document).on('click', '.each_chart10', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/10", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/10", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart11', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/11", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/11", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart12', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/12", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/12", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart13', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/13", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/13", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart14', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/14", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/14", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart15', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/15", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/15", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart16', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/16", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/16", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart17', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/17", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/17", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart18', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/18", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/18", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }
    })
});
$(document).on('click', '.each_chart19', function (event) {
    main_id = $(this).attr('class').slice(10, )
    // $.get("http://127.0.0.1:8000/eachchart_options/19", function (data1, status) {
        $.get("http://akatsuki-opvdata.com/eachchart_options/19", function (data1, status) {
        for (let key in data1) {
            myFunc(data1[key]);
        }

    })
});


$(document).on('click', '.js-plotly-plot', function (event) {
    if (main_id < 10) {
        var id = $(this).attr('id');
        // $.get("http://127.0.0.1:8000/eachchart/" + main_id, function (data2, status) {
            $.get("http://akatsuki-opvdata.com/eachchart/" + main_id, function (data2, status) {
            Func1(data2, id);
        })
    } else if (main_id > 9) {
        $(document).on('click', '.js-plotly-plot', function (event) {
            var id = $(this).attr('id');
            // $.get("http://127.0.0.1:8000/eachchart_options/" + main_id, function (data2, status) {
                $.get("http://akatsuki-opvdata.com/eachchart_options/" + main_id, function (data2, status) {
                Func2(data2, id);
            })
        });
    }
});
