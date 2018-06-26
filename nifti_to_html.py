import base64
import sys
import argparse
import json

import numpy as np
from nilearn import surface, datasets
from nilearn import plotting
import matplotlib as mpl
from matplotlib import cm

HTML_TEMPLATE = """

<html>

<head>
    <title>surface plot</title>
    <meta charset="UTF-8" />
    <script src="https://cdn.plot.ly/plotly-gl3d-latest.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js">
    </script>
    <script>
        function decodeBase64(encoded, dtype) {

            let getter = {
                "float32": "getFloat32",
                "int32": "getInt32"
            }[dtype];

            let arrayType = {
                "float32": Float32Array,
                "int32": Int32Array
            }[dtype];

            let raw = atob(encoded)
            let buffer = new ArrayBuffer(raw.length);
            let asIntArray = new Uint8Array(buffer);
            for (let i = 0; i !== raw.length; i++) {
                asIntArray[i] = raw.charCodeAt(i);
            }

            let view = new DataView(buffer);
            let decoded = new arrayType(
                raw.length / arrayType.BYTES_PER_ELEMENT);
            for (let i = 0, off = 0; i !== decoded.length;
                i++, off += arrayType.BYTES_PER_ELEMENT) {
                decoded[i] = view[getter](off, true);
            }
            return decoded;
        }

        var surfaceMapInfo = INSERT_STAT_MAP_JSON_HERE;
        var colorscale = INSERT_COLORSCALE_HERE;

        function addPlot() {

            let hemisphere = $("#select-hemisphere").val();
            let kind = $("#select-kind").val();
            makePlot(kind, hemisphere,
                     "surface-plot", display = null, erase = true);
        }

        function makePlot(surface, hemisphere, divId) {

            info = surfaceMapInfo[surface + "_" + hemisphere];

            info["type"] = "mesh3d";


            for (let attribute of ["x", "y", "z"]) {
                if (!(attribute in info)) {
                    info[attribute] = decodeBase64(
                        info["_" + attribute], "float32");
                }
            }

            for (let attribute of ["i", "j", "k"]) {
                if (!(attribute in info)) {
                    info[attribute] = decodeBase64(
                        info["_" + attribute], "int32");
                }
            }

            info["vertexcolor"] = surfaceMapInfo["vertexcolor_" + hemisphere];
            console.log(info["vertexcolor"]);

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

            let camera = getCamera();

            info['lighting'] = {
                "ambient": 0.5,
                "diffuse": 1,
                "fresnel": .1,
                "specular": .05,
                "roughness": .1,
                "facenormalsepsilon": 1e-6,
                "vertexnormalsepsilon": 1e-12
            };

            let layout = {
                width: $(window).width() * .8,
                height: $(window).outerHeight() * .8,
                hovermode: false,
                paper_bgcolor: '#fff',
                axis_bgcolor: '#333',
                scene: {
                    camera: camera,
                    xaxis: axisConfig,
                    yaxis: axisConfig,
                    zaxis: axisConfig
                }
            };

            let config = {
                modeBarButtonsToRemove: ["hoverClosest3d"],
                displayLogo: false
            };


            Plotly.react(divId, data, layout, config);

            // hack to get a colorbar
            dummy = {
                "opacity": 0,
                "type": "mesh3d",
                "colorscale": colorscale,
                "x": [1, 0, 0],
                "y": [0, 1, 0],
                "z": [0, 0, 1],
                "i": [0],
                "j": [1],
                "k": [2],
                "intensity": [0.],
                "cmin": surfaceMapInfo["cmin"],
                "cmax": surfaceMapInfo["cmax"]
            };

            Plotly.plot(divId, [dummy], layout, config);
        }

        function getCamera() {
            let view = $("#select-view").val();
            if (view === "custom") {
                try {
                    return $("#surface-plot")[0].layout.scene.camera;
                } catch (e) {
                    return {};
                }
            }
            let cameras = {
                "left": {eye: {x: -2, y: 0, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}
                },
                "right": {eye: {x: 2, y: 0, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}
                },
                "top": {eye: {x: 0, y: 0, z: 2},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}
                },
                "bottom": {eye: {x: 0, y: 0, z: -2},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}
                },
                "front": {eye: {x: 0, y: 2, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}
                },
                "back": {eye: {x: 0, y: -2, z: 0},
                    up: {x: 0, y: 0, z: 1},
                    center: {x: 0, y: 0, z: 0}
                },
            };
            return cameras[view];

        }
    </script>
    <script>
        $(document).ready(
            function() {
                addPlot();
                $("#select-hemisphere").change(addPlot);
                $("#select-kind").change(addPlot);
                $("#select-view").change(addPlot);
                $("#surface-plot").mouseup(function() {
                    $("#select-view").val("custom");
                });
                $(window).resize(addPlot);

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
    <select id="select-view">
<option value="left">view: Left</option>
<option value="right">view: Right</option>
<option value="front">view: Front</option>
<option value="back">view: Back</option>
<option value="top">view: Top</option>
<option value="bottom">view: Bottom</option>
<option value="custom">-</option>
</select>

</body>

</html>

"""


def colorscale(cmap, values, threshold=None):
    cmap = cm.get_cmap(cmap)
    abs_values = np.abs(values)
    abs_max = abs_values.max()
    norm = mpl.colors.Normalize(vmin=-abs_max, vmax=abs_max)
    cmaplist = [cmap(i) for i in range(cmap.N)]
    abs_threshold = None
    if threshold is not None:
        abs_threshold = np.percentile(abs_values, threshold)
        istart = int(norm(-abs_threshold, clip=True) * (cmap.N - 1))
        istop = int(norm(abs_threshold, clip=True) * (cmap.N - 1))
        for i in range(istart, istop):
            cmaplist[i] = (0.5, 0.5, 0.5, 1.)  # just an average gray color
    our_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'Custom cmap', cmaplist, cmap.N)
    x = np.linspace(0, 1, 100)
    rgb = our_cmap(x, bytes=True)[:, :3]
    rgb = np.array(rgb, dtype=int)
    colors = []
    for i, col in zip(x, rgb):
        colors.append([np.round(i, 3), "rgb({}, {}, {})".format(*col)])
    return json.dumps(colors), abs_max, our_cmap, norm, abs_threshold


def _encode(a):
    return base64.b64encode(a.tobytes()).decode('utf-8')


def to_plotly(mesh):
    mesh = surface.load_surf_mesh(mesh)
    x, y, z = map(_encode, np.asarray(mesh[0].T, dtype='<f4'))
    i, j, k = map(_encode, np.asarray(mesh[1].T, dtype='<i4'))
    info = {
        "_x": x,
        "_y": y,
        "_z": z,
        "_i": i,
        "_j": j,
        "_k": k,
    }
    return info


def load_fsaverage():
    return {
        'pial_left':
        '/home/jerome/workspace/scratch/fsaverage/pial_left.gii',
        'infl_left':
        '/home/jerome/workspace/scratch/fsaverage/inflated_left.gii',
        'pial_right':
        '/home/jerome/workspace/scratch/fsaverage/pial_right.gii',
        'infl_right':
        '/home/jerome/workspace/scratch/fsaverage/inflated_right.gii',
        'sulc_right':
        '/home/jerome/workspace/scratch/fsaverage/sulc_right.gii',
        'sulc_left':
        '/home/jerome/workspace/scratch/fsaverage/sulc_left.gii'
    }


def full_brain_info(stat_map, threshold=None):
    info = {}
    fsaverage = datasets.fetch_surf_fsaverage5()
    # fsaverage = load_fsaverage()
    surf_maps = [
        surface.vol_to_surf(stat_map, fsaverage['pial_{}'.format(h)])
        for h in ['left', 'right']
    ]
    colors, cmax, cmap, norm, at = colorscale(plotting.cm.cold_hot,
                                              np.asarray(surf_maps).ravel(),
                                              threshold)

    for hemi in ['left', 'right']:
        pial = fsaverage['pial_{}'.format(hemi)]
        surf_map = surface.vol_to_surf(stat_map, pial)
        surf_maps.append(surf_map)
        sulc_depth_map = surface.load_surf_data(
            fsaverage['sulc_{}'.format(hemi)])
        sulc_depth_map -= sulc_depth_map.min()
        sulc_depth_map /= sulc_depth_map.max()
        info['pial_{}'.format(hemi)] = to_plotly(pial)
        info['inflated_{}'.format(hemi)] = to_plotly(
            fsaverage['infl_{}'.format(hemi)])
        vertexcolor = cmap(norm(surf_map).data)
        if threshold is not None:
            anat_color = cm.get_cmap('Greys')(sulc_depth_map)
            vertexcolor[np.abs(surf_map) < at] = anat_color[
                np.abs(surf_map) < at]
        vertexcolor = np.asarray(vertexcolor * 255, dtype='uint8')
        info['vertexcolor_{}'.format(hemi)] = [
            '#{:02x}{:02x}{:02x}'.format(*row) for row in vertexcolor
        ]
    colors, cmax, cmap, norm, at = colorscale(plotting.cm.cold_hot,
                                              np.asarray(surf_maps).ravel(),
                                              threshold)
    info["cmin"], info["cmax"] = -cmax, cmax
    return info, colors


def make_html(stat_map=None, threshold=None):
    if stat_map is None:
        stat_map = datasets.fetch_localizer_button_task()['tmaps'][0]
    info, colors = full_brain_info(stat_map, threshold)
    as_json = json.dumps(info)
    as_html = HTML_TEMPLATE.replace('INSERT_STAT_MAP_JSON_HERE', as_json)
    as_html = as_html.replace('INSERT_COLORSCALE_HERE', colors)
    return as_html


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stat_map', type=str, default=None)
    parser.add_argument('--threshold', type=int, default=None)
    parser.add_argument(
        '--out_file', type=str, default='surface_plot_standalone.html')
    args = parser.parse_args()
    as_html = make_html(args.stat_map, args.threshold)
    with open(args.out_file, 'w') as f:
        f.write(as_html)
