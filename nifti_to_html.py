import sys
import argparse
import json

import numpy as np
from nilearn import surface, datasets

HTML_TEMPLATE = """
<html>

<head>
    <title>surface plot</title>
    <meta charset="UTF-8" />
    <script src="https://cdn.plot.ly/plotly-gl3d-latest.min.js"></script>
    <script
        src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js">
    </script>
    <script>
        function addPlot() {

            let surface_map_info = INSERT_STAT_MAP_JSON_HERE;
            let hemisphere = $("#select-hemisphere").val();
            let kind = $("#select-kind").val();
            makePlot(
                surface_map_info[kind + "_" + hemisphere], "surface-plot");
        }

        function makePlot(info, divId) {

            info["type"] = "mesh3d";

            info["colorscale"] = [
                [0.0, "rgb(255, 255, 255)"],
                [0.111, "rgb(34, 255, 255)"],
                [0.222, "rgb(0, 131, 255)"],
                [0.333, "rgb(0, 0, 233)"],
                [0.444, "rgb(0, 0, 86)"],
                [0.556, "rgb(86, 0, 0)"],
                [0.667, "rgb(233, 0, 0)"],
                [0.778, "rgb(255, 131, 0)"],
                [0.889, "rgb(255, 255, 34)"],
                [1.0, "rgb(255, 255, 255)"]
            ];

            let data = [info];
            let axisConfig = {
                showgrid: false,
                showline: false,
                ticks: '',
                showticklabels: false,
                zeroline: false,
                showspikes: false,
                spikesides: false
            };

            let x = 2;

            if($("#select-hemisphere").val() === 'left'){
                x = -2;
            }

  info['lighting'] = {"ambient": 0.5,
            "diffuse": 1,
            "fresnel":  .1,
            "specular": .05,
            "roughness": .1,
            "facenormalsepsilon": 1e-6,
            "vertexnormalsepsilon": 1e-12};

            let layout = {
                width: 800,
                height: 800,
                hovermode: false,
                paper_bgcolor: '#333',
                axis_bgcolor: '#333',
                scene: {
                    camera: {eye: {x: x, y: 0, z: 0},
                             up: {x: 0, y: 0, z: 1},
                             center: {x: 0, y: 0, z: 0}},
                    xaxis: axisConfig,
                    yaxis: axisConfig,
                    zaxis: axisConfig
                }
            };

    let config = {
        modeBarButtonsToRemove: ["hoverClosest3d"], displayLogo: false
    };

            Plotly.react(divId, data, layout, config);
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


def colorscale(cm):
    x = np.linspace(0, 1, 10)
    rgb = cm(x, bytes=True)[:, :3]
    rgb = np.array(rgb, dtype=int)
    colors = []
    for i, col in zip(x, rgb):
        colors.append([np.round(i, 3), "rgb({}, {}, {})".format(*col)])
    return json.dumps(colors)


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


def load_fsaverage():
    return {
        'pial_left': '/home/jerome/workspace/scratch/fsaverage/pial_left.gii',
        'infl_left': '/home/jerome/workspace/scratch/fsaverage/inflated_left.gii',
        'pial_right': '/home/jerome/workspace/scratch/fsaverage/pial_right.gii',
        'infl_right': '/home/jerome/workspace/scratch/fsaverage/inflated_right.gii'

            }

def full_brain_info(stat_map, threshold=None):
    info = {}
    # fsaverage = datasets.fetch_surf_fsaverage5()
    fsaverage = load_fsaverage()
    for hemi in ['left', 'right']:
        pial = fsaverage['pial_{}'.format(hemi)]
        surf_map = surface.vol_to_surf(stat_map, pial)
        if threshold is not None:
            abs_threshold = np.percentile(np.abs(surf_map), threshold)
            surf_map[np.abs(surf_map) < abs_threshold] = np.nan
        info['pial_{}'.format(hemi)] = to_plotly(pial, surf_map)
        info['inflated_{}'.format(hemi)] = to_plotly(
            fsaverage['infl_{}'.format(hemi)], surf_map)
    return info


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stat_map', type=str, default=None)
    parser.add_argument('--threshold', type=int, default=None)
    parser.add_argument(
        '--out_file', type=str, default='surface_plot_standalone.html')
    args = parser.parse_args()
    if args.stat_map is not None:
        stat_map = args.stat_map
    else:
        stat_map = datasets.fetch_localizer_button_task()['tmaps'][0]
    as_json = json.dumps(full_brain_info(stat_map, args.threshold))
    as_html = HTML_TEMPLATE.replace('INSERT_STAT_MAP_JSON_HERE', as_json)
    with open(args.out_file, 'w') as f:
        f.write(as_html)
