import argparse
import json

from nilearn import surface, datasets


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stat_map', type=str)
    args = parser.parse_args()

    fsaverage = datasets.fetch_surf_fsaverage5()
    mesh = fsaverage['pial_left']
    surf_map = surface.vol_to_surf(args.stat_map, mesh)
    as_json = to_plotly(mesh, surf_map, 'info.json')
