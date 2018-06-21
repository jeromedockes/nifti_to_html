function addPlotToDiv(divId) {

    $.ajax({
        url: 'info.json',
        mimeType: "application/json",
        dataType: "json",
        success: function(info) {
            console.log(info);
            makePlot(info, divId);}
    });

}

function makePlot(info, divId){

    info["type"] = "mesh3d";
    info["colorscale"] = [
        [0, 'rgb(0, 0, 255)'],
        [0.2, 'rgb(20, 0, 230)'],
        [0, 'rgb(20, 0, 230)'],
        [1, 'rgb(255, 0, 0)']
    ];

    var data = [ info ];
    var axisConfig = {showgrid: false,
                      showline: false, ticks: '',
                      showticklabels: false,
                      zeroline: false};
    var layout = {
        width: 1000,
        height: 1000,
        scene: {
            xaxis: axisConfig,
            yaxis: axisConfig,
            zaxis: axisConfig
        }
    };

    Plotly.react('surface-plot', data, layout);
}
