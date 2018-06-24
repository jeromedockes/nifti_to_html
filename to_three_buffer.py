import base64
import argparse
import json

import numpy as np
from nilearn import surface, datasets
from nilearn.plotting import cm


HTML_TEMPLATE = """

<html>

    <head>
        <title>surface plot</title>
        <meta charset="UTF-8"/>


        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/build/three.min.js"></script> -->
        <!-- <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script> -->
        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/build/three.js"></script> -->
        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/Detector.js"></script> -->
        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/libs/stats.min.js"></script> -->
        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/controls/OrbitControls.js"></script> -->
        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/controls/TrackballControls.js"></script> -->
        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/math/Lut.js"></script> -->


        <script src="file:///home/jerome/workspace/scratch/cdn/jquery.min.js"></script>
        <script src="file:///home/jerome/workspace/scratch/cdn/three.js"></script>
        <script src="file:///home/jerome/workspace/scratch/cdn/Detector.js"></script>
        <script src="file:///home/jerome/workspace/scratch/cdn/stats.min.js"></script>
        <script src="file:///home/jerome/workspace/scratch/cdn/OrbitControls.js"></script>
        <script src="file:///home/jerome/workspace/scratch/cdn/TrackballControls.js"></script>
        <script src="file:///home/jerome/workspace/scratch/cdn/Lut.js"></script>

</head>
<script>
function addPlot(){

		var camera, scene, renderer, controls, directionalLight0;
			init();
			animate();


			function init() {
				  camera = new THREE.PerspectiveCamera(
              45, window.innerWidth / window.innerHeight, 1, 2000 );
				camera.position.x = -300;
				scene = new THREE.Scene();
let position = INSERT_CENTER_POSITION_HERE;
scene.position.x = position.x;
scene.position.y = position.y;
scene.position.z = position.z;
				  scene.background = new THREE.Color( 0x555555 );
				var ambient = new THREE.AmbientLight( 0xaaaaaa );
				scene.add( ambient );


				directionalLight0 = new THREE.DirectionalLight( 0xffffff );
				  directionalLight0.position.x = -400;
				scene.add( directionalLight0 );

          var geometry = new THREE.BufferGeometry();

var raw = atob("INSERT_VERTICES_HERE")
var buffer = new ArrayBuffer(raw.length);
 var array = new Uint8Array(buffer);
for(let i = 0; i < raw.length; i++) {
    array[i] = raw.charCodeAt(i);
}
var view = new DataView(buffer);
var vertices = new Float32Array(raw.length / 4);
console.log(vertices.length);
for(let i=0, off = 0; i < vertices.length; i++, off += 4){
vertices[i] = view.getFloat32(off, true);
}
          // itemSize = 3 because there are 3 values (components) per vertex

var colors = new Float32Array( INSERT_COLORS_HERE );
					geometry.addAttribute( 'color', new THREE.BufferAttribute( new Float32Array( colors ), 3 ) );
          geometry.addAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
          geometry.computeVertexNormals();
// normalize normals?
          // var material = new THREE.MeshBasicMaterial( { color: 0xff0000 } );
var material = new THREE.MeshLambertMaterial( {
						side: THREE.DoubleSide,
						color: 0xF5F5F5,
						vertexColors: THREE.VertexColors
					} );

          var mesh = new THREE.Mesh( geometry, material );

				 	scene.add( mesh );
          console.log(mesh);
				// var objectLoader = new THREE.ObjectLoader();
				// objectLoader.load("brain.json", function ( obj ) {
             mesh.rotation.x = -90 * Math.PI / 180;
              mesh.rotation.z = 180 * Math.PI / 180;
        //     obj.geometry.computeVertexNormals();
        //     console.log(obj)

				// } );

				  // var controls = new THREE.OrbitControls( camera );

           controls = new THREE.TrackballControls( camera );
				   controls.rotateSpeed = 7.0;
				   controls.zoomSpeed = 1.2;
				   controls.panSpeed = 0.8;
				   controls.noZoom = false;
				   controls.noPan = false;
				   controls.staticMoving = true;
				   controls.dynamicDampingFactor = 0.3;
				   controls.keys = [ -29, -21, 17 ];
				   controls.addEventListener( 'change', render );

				renderer = new THREE.WebGLRenderer();
				renderer.setSize( window.innerWidth * .7, window.innerHeight * .7 );
          $("body").append(renderer.domElement);
        //
			}
			//
			function animate() {
           controls.update();
          requestAnimationFrame( animate );
          render();
			}

			function render() {
				  // camera.lookAt( scene.position );

                directionalLight0.position.x = camera.position.x;
                renderer.render( scene, camera );
			}

		}

$(document).ready(addPlot);







</script>
    </head>
    <body>


    </body>

</html>

"""


def to_three(mesh, stat_map, sample_mesh=None):
    if sample_mesh is None:
        sample_mesh = mesh
    mesh = surface.load_surf_mesh(mesh)
    coords = mesh[0][mesh[1].ravel()]
    surf_stat_map = surface.vol_to_surf(stat_map, sample_mesh)
    surf_stat_map -= surf_stat_map.min()
    surf_stat_map /= surf_stat_map.max()
    colors = cm.cold_hot(surf_stat_map[mesh[1].ravel()])[:, :3]
    center = list(map(float, mesh[0].mean(axis=0)))
    center = {'x': center[0], 'y': center[1], 'z': center[2]}
    vertices = np.asarray(coords.ravel(), dtype='<f4')
    # vertices = list(map(float, coords.ravel()))
    col = list(map(float, colors.ravel()))
    return {
        'INSERT_VERTICES_HERE': base64.b64encode(vertices.tobytes()).decode('utf-8'), #json.dumps(vertices),
        'INSERT_COLORS_HERE': json.dumps(col),
        'INSERT_CENTER_POSITION_HERE': json.dumps(center)
    }


def load_fsaverage():
    return {
        'pial_left': '/home/jerome/workspace/scratch/fsaverage/pial_left.gii',
        'infl_left': '/home/jerome/workspace/scratch/fsaverage/inflated_left.gii',
        'pial_right': '/home/jerome/workspace/scratch/fsaverage/pial_right.gii',
        'infl_right': '/home/jerome/workspace/scratch/fsaverage/inflated_right.gii'

            }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out_file', type=str, default='surface_plot_standalone.html')
    args = parser.parse_args()

    # fsaverage = datasets.fetch_surf_fsaverage5()
    fsaverage = load_fsaverage()
    stat_map = datasets.fetch_localizer_button_task()['tmaps'][0]
    as_json = to_three(
        fsaverage['pial_right'], stat_map, fsaverage['pial_right'])
    as_html = HTML_TEMPLATE
    for k, v in as_json.items():
        as_html = as_html.replace(k, v)
    with open(args.out_file, 'w') as f:
        f.write(as_html)
