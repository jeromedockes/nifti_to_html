import json

import numpy as np
from nilearn import datasets, surface


def to_three(vertices, triangles):
    print(vertices.mean(axis=0))
    geometry_id, object_id, material_id = 'G', 'O', 'M'
    three = {'metadata': {'type': 'Object'}}
    three['object'] = {
        'castShadow': True,
        'geometry': geometry_id,
        'material': material_id,
        'matrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        'name': 'mesh',
        'receiveShadow': True,
        'type': 'Mesh',
        'uuid': object_id
    }
    three['materials'] = [{
        'ambient': 16714940,
        'color': 11111111,
        'emissive': 0,
        'opacity': 1,
        'shininess': 50,
        'specular': 0.05,
        'transparent': False,
        'type': 'MeshPhongMaterial',
        'uuid': material_id,
        'wireframe': False
    }]
    geometry = {'uuid': geometry_id, 'type': 'Geometry'}
    # geometry['data'] = {'normals': [], 'uvs': []}
    geometry['data'] = {}
    geometry['data']['vertices'] = list(map(float, vertices.ravel()))
    intensity = vertices[:, 0]
    three['object']['userData'] = {'intensity': list(map(float, intensity))}
    t = np.zeros((triangles.shape[0], 4), dtype=int)
    t[:, 1:] = triangles
    geometry['data']['faces'] = list(map(int, t.ravel()))
    three['geometries'] = [geometry]
    return json.dumps(three)


def load_fsaverage():
    return {
        'pial_left': '/home/jerome/workspace/scratch/fsaverage/pial_left.gii',
        'infl_left': '/home/jerome/workspace/scratch/fsaverage/inflated_left.gii',
        'pial_right': '/home/jerome/workspace/scratch/fsaverage/pial_right.gii',
        'infl_right': '/home/jerome/workspace/scratch/fsaverage/inflated_right.gii'

            }


if __name__ == '__main__':
    fsaverage = load_fsaverage()
    fsaverage = datasets.fetch_surf_fsaverage5()
    mesh = surface.load_surf_mesh(fsaverage['pial_left'])
    three = to_three(*mesh)
    with open('brain.json', 'w') as f:
        f.write(three)
