function addPlot(){

		var camera, scene, renderer, controls;
			init();
			animate();


			function init() {
          // camera
				  camera = new THREE.PerspectiveCamera(
              45, window.innerWidth / window.innerHeight, 1, 2000 );
				camera.position.x = 400;
				// scene
				scene = new THREE.Scene();
				var ambient = new THREE.AmbientLight( 0x777777 );
				scene.add( ambient );

				var directionalLight = new THREE.DirectionalLight( 0xffeedd );
				directionalLight.position.set( 0, 0, -1 ).normalize();
				scene.add( directionalLight );

				  var directionalLight1 = new THREE.DirectionalLight( 0xffeedd );
				  directionalLight.position.set( 0, 1, 0 ).normalize();
				  scene.add( directionalLight1 );


				  var directionalLight2 = new THREE.DirectionalLight( 0xffeedd );
				  directionalLight.position.set( 1, 0, 0 ).normalize();
				  scene.add( directionalLight2 );


				var objectLoader = new THREE.ObjectLoader();
				objectLoader.load("brain.json", function ( obj ) {
            obj.geometry.computeVertexNormals();
				 	scene.add( obj );
				} );

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
