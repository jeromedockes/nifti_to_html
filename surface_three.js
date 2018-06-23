function addPlot(){

		var camera, scene, renderer, controls;
			init();
			animate();


			function init() {
          // camera
				  camera = new THREE.PerspectiveCamera(
              45, window.innerWidth / window.innerHeight, 1, 2000 );
				camera.position.z = 30;
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
          var vertices = new Float32Array( [
	            -1.0, -1.0,  1.0,
	            1.0, -1.0,  1.0,
	            1.0,  1.0,  1.0,

	            1.0,  1.0,  1.0,
	            -1.0,  1.0,  1.0,
	            -1.0, -1.0,  1.0,

	                  ] );

          // itemSize = 3 because there are 3 values (components) per vertex
          geometry.addAttribute( 'position', new THREE.BufferAttribute( vertices, 3 ) );
          geometry.computeVertexNormals();
          geometry.normalizeVertexNormals();
          var material = new THREE.MeshBasicMaterial( { color: 0xff0000 } );
          var mesh = new THREE.Mesh( geometry, material );

				 	scene.add( mesh );
          console.log(mesh);
				// var objectLoader = new THREE.ObjectLoader();
				// objectLoader.load("brain.json", function ( obj ) {
        //     obj.rotation.x = -90 * Math.PI / 180;
        //     obj.geometry.computeVertexNormals();
        //     console.log(obj)

				// } );

				  var controls = new THREE.OrbitControls( camera );

          // controls = new THREE.TrackballControls( camera );
				  // controls.rotateSpeed = 7.0;
				  // controls.zoomSpeed = 1.2;
				  // controls.panSpeed = 0.8;
				  // controls.noZoom = false;
				  // controls.noPan = false;
				  // controls.staticMoving = true;
				  // controls.dynamicDampingFactor = 0.3;
				  // controls.keys = [ -29, -21, 17 ];
				  // controls.addEventListener( 'change', render );

				renderer = new THREE.WebGLRenderer();
				renderer.setSize( window.innerWidth * .7, window.innerHeight * .7 );
          $("body").append(renderer.domElement);
        //
			}
			//
			function animate() {
          // controls.update();
          requestAnimationFrame( animate );
          render();
			}

			function render() {
				  // camera.lookAt( scene.position );
				renderer.render( scene, camera );
			}

		}

$(document).ready(addPlot);
