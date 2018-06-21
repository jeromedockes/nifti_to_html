import argparse
import json

from nilearn import surface, datasets

HTML_TEMPLATE = """
<html>
    <head>
        <title>surface plot</title>
        <meta charset="UTF-8" />
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <script>

function addPlot() {

            let surface_map_info = INSERT_STAT_MAP_JSON_HERE;
let hemisphere = $("#select-hemisphere").val();
let kind = $("#select-kind").val();
            makePlot(surface_map_info[kind + "_" + hemisphere], "surface-plot");
}

function makePlot(info, divId){

    info["type"] = "mesh3d";
    info["colorscale"] = [
        [0, 'rgb(0, 0, 255)'],
        [0.2, 'rgb(20, 0, 230)'],
        [0, 'rgb(20, 0, 230)'],
        [1, 'rgb(255, 0, 0)']
    ];

    let data = [ info ];
    let axisConfig = {showgrid: false,
                      showline: false, ticks: '',
                      showticklabels: false,
                      zeroline: false};
    let layout = {
        width: 1000,
        height: 1000,
        scene: {
            xaxis: axisConfig,
            yaxis: axisConfig,
            zaxis: axisConfig
        }
    };

    Plotly.react(divId, data, layout);
}

        </script>
        <script>
$(document).ready(
function() {
addPlot();
$("#select-hemisphere").change(addPlot)
$("#select-kind").change(addPlot)

});

</script>
    </head>
    <body>
        <div id="surface-plot"></div>
<select id="select-hemisphere">
<option value="left">Left hemisphere</option>
<option value="right">Right hemisphere</option>
</select>

<select id="select-kind">
<option value="inflated">Inflated</option>
<option value="pial">Pial</option>
</select>

    </body>
</html>


"""


def to_plotly(mesh, stat_map, out_file=None):
    mesh = surface.load_surf_mesh(mesh)
    x, y, z = map(list, mesh[0].T)
    i, j, k = map(list, mesh[1].T)
    info = {
        "x": x,
        "y": y,
        "z": z,
        "i": i,
        "j": j,
        "k": k,
        "intensity": stat_map
    }
    info = {k: [float(e) for e in v] for k, v in info.items()}
    if out_file is None:
        return info
    json_info = json.dumps(info)
    with open(out_file, 'wb') as f:
        f.write(json_info.encode('utf-8'))
    return info


def full_brain_info(stat_map):
    info = {}
    fsaverage = datasets.fetch_surf_fsaverage5()
    for hemi in ['left', 'right']:
        pial = fsaverage['pial_{}'.format(hemi)]
        surf_map = surface.vol_to_surf(stat_map, pial)
        info['pial_{}'.format(hemi)] = to_plotly(pial, surf_map)
        info['inflated_{}'.format(hemi)] = to_plotly(
            fsaverage['infl_{}'.format(hemi)], surf_map)
    return info


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stat_map', type=str)
    parser.add_argument(
        '--out_file', type=str, default='surface_plot_standalone.html')
    args = parser.parse_args()
    as_json = json.dumps(full_brain_info(args.stat_map))
    as_html = HTML_TEMPLATE.replace('INSERT_STAT_MAP_JSON_HERE', as_json)
    with open(args.out_file, 'w') as f:
        f.write(as_html)
