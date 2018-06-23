import sys
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
        <script
            src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <!-- <script src="https://cdn.rawgit.com/mrdoob/three.js/master/build/three.min.js"></script> -->
 <script src="https://cdn.rawgit.com/mrdoob/three.js/master/build/three.js"></script>
    <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/Detector.js"></script>
    <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/libs/stats.min.js"></script>
    <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/controls/TrackballControls.js"></script>
    <script src="https://cdn.rawgit.com/mrdoob/three.js/master/examples/js/math/Lut.js"></script>
        <script>



function addPlot(){

		var camera, scene, renderer, controls;
			init();
			animate();


			function init() {
          // camera
				  camera = new THREE.PerspectiveCamera(
              45, window.innerWidth / window.innerHeight, 1, 2000 );
				camera.position.x = -300;
        // camera.rotation.x = -90 * Math.PI / 180;
        // scene
				scene = new THREE.Scene();
				  scene.background = new THREE.Color( 0x555555 );
				var ambient = new THREE.AmbientLight( 0xaaaaaa );
				scene.add( ambient );


				var directionalLight0 = new THREE.DirectionalLight( 0xffffff );
				  directionalLight0.position.x = -400;
				scene.add( directionalLight0 );

				  // var directionalLight1 = new THREE.DirectionalLight( 0xffffff );
				  // directionalLight1.position.x = 400;
				  // scene.add( directionalLight1 );


          var geometry = new THREE.BufferGeometry();
          // create a simple square shape. We duplicate the top left and bottom right
          // vertices because each vertex needs to appear once per triangle.
          var vertices = new Float32Array(
INSERT_VERTICES_HERE
	                   );

          // itemSize = 3 because there are 3 values (components) per vertex

var colors = new Float32Array( INSERT_COLORS_HERE );
					geometry.addAttribute( 'color', new THREE.BufferAttribute( new Float32Array( colors ), 3 ) );
          geometry.addAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
          geometry.computeVertexNormals();
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
        //     obj.rotation.x = -90 * Math.PI / 180;
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


def to_three(mesh, stat_map):
    mesh = surface.load_surf_mesh(mesh)
    coords = mesh[0][mesh[1].ravel()]
    surf_stat_map = surface.vol_to_surf(stat_map, mesh)
    surf_stat_map -= surf_stat_map.min()
    surf_stat_map /= surf_stat_map.max()
    print(surf_stat_map)
    colors = cm.cold_hot(surf_stat_map[mesh[1].ravel()])[:, :3]
    print(colors[:20])
    return list(map(float, coords.ravel())), list(map(float, colors.ravel()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out_file', type=str, default='surface_plot_standalone.html')
    args = parser.parse_args()

    fsaverage = datasets.fetch_surf_fsaverage5()
    stat_map = datasets.fetch_localizer_button_task()['tmaps'][0]
    as_json = list(
        map(json.dumps, to_three(fsaverage['pial_right'], stat_map)))
    as_html = HTML_TEMPLATE.replace('INSERT_VERTICES_HERE', as_json[0])
    as_html = as_html.replace('INSERT_COLORS_HERE', as_json[1])
    with open(args.out_file, 'w') as f:
        f.write(as_html)
