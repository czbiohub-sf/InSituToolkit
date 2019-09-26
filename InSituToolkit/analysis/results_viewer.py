import argparse
from itertools import cycle

import numpy as np
import napari
import pandas as pd
from skimage import io
from starfish import Experiment, IntensityTable
from starfish.types import Axes

def _parse_args():
    """
    Parse arguments for the CLI
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--fovs',
        type=str,
        required=True,
        help="Path to the fov data",
    )
    parser.add_argument(
        '--exp',
        type=str,
        required=True,
        help="Path to experiment file",
    )

    return parser.parse_args()


def _make_points_array(it: IntensityTable, channel: int):
    """
    Creates the array of spot coordinates for the napari points layer

    Parameters
    ----------
    it : IntensityTable
            IntensityTable containing the spots
    channel : int
            Channel index for the spots

    Returns
    -------
    point_coords : np.ndarray
            Array of coordinates for the spots

    """
    coords = zip(it.x.values, it.y.values)
    point_coords = np.asarray([[channel, y, x] for x, y in coords])
    
    return point_coords


def _get_points(it, exp):
    """
    Creates a list of point coordinates 

    Parameters
    ----------
    it : IntensityTable
            IntensityTable containing the spots
    exp : Experiment
            Experiment file corresponding to the data analysis

    Returns
    -------
    points : List[Dict]
            List of dictionaries containing the points and target names for the
            points to be rendered

    """
    # Get the codes and targets
    codebook = exp.codebook
    targets = list(codebook.target.values)

    points = []
    for i, t in enumerate(targets):
        spots = it.where(it.target == t, drop=True)
        code = codebook.where(codebook.target == t, drop=True).data
        channel = int(np.nonzero(np.squeeze(code))[0])
        point_coords = _make_points_array(spots, channel)
        point_data = {
                    'coords': point_coords,
                    'name': t
        }
        points.append(point_data)

    return points


def _load_data(fov_data, exp):
    """
    Load a field of view dataset 

    Parameters
    ----------
    fov_data : pd.DataFrame
            Table of file locations for the spot results and mask label image
            corresponding to the dataset to be viewed
    exp : Experiment
            Experiment file corresponding to the data analysis

    Returns
    -------
    im_max_proj : np.ndarray
            Image used for the spot detection
    points : List[Dict]
            List of dictionaries containing the points and target names for the
            points to be rendered
    mask_im : np.ndarray
            Label image for the segmentation mask 

    """
    # Get the RNAscope images
    im = exp[fov_data.fov_name].get_image("primary")
    im_max_proj = np.squeeze(im.max_proj(Axes.ZPLANE).xarray.values)

    # Get the spots
    spots_file = fov_data.spot_file
    it = IntensityTable.open_netcdf(spots_file)
    
    points = _get_points(it, exp)

    # Get the segmentation mask
    mask_file = fov_data.mask_file
    mask_im = io.imread(mask_file)
    
    return im_max_proj, points, mask_im


def view_results(fov_df, exp):
    """
    Create the napari GUI that displays the image data overlayed with the
    segmentation mask and detected spots. The GUI displays one field of view
    at a time. The user can increment the field of view with the '.' key and
    decremented with the ',' key.

    Parameters
    ----------
    fov_df : pd.DataFrame
            Table of file locations for the spot results and mask label images
            for all fields of view to be displayed
    exp : Experiment
            Experiment file corresponding to the data analysis

    """
    # Get the indices
    indices = fov_df.index.values
    n_fov = len(indices)
    
    with napari.gui_qt():
        index = 0
        colors = cycle('wgmcykb')
        viewer = napari.Viewer()
        
        fov_data = fov_df.loc[index]
        im_max_proj, points, mask = _load_data(fov_data, exp)

        metadata = {'index': index}
        viewer.add_image(im_max_proj, name=fov_data['fov_name'], metadata=metadata)
        viewer.add_labels(mask, name='Segmentation Mask')

        for point in points:
            viewer.add_points(
                point['coords'],
                name=point['name'],
                symbol='ring',
                face_color=next(colors)
            )
        
        viewer.status = str(index)
        
        @viewer.bind_key('.')
        def next_image(viewer):
            index = viewer.layers[0].metadata['index']
            index += 1
            viewer.layers[0].metadata['index'] = index
            
            new_fov = fov_df.loc[(index + n_fov)%n_fov]
            update_viewer(viewer, new_fov)

        @viewer.bind_key(',')
        def previous_image(viewer):
            index = viewer.layers[0].metadata['index']
            index -= 1
            viewer.layers[0].metadata['index'] = index
            
            new_fov = fov_df.loc[(index + n_fov)%n_fov]
            update_viewer(viewer, new_fov)
            
            
        def update_viewer(viewer, new_fov):
            im_max_proj, points, mask = _load_data(new_fov, exp)
            
            viewer.layers[0].data = im_max_proj
            viewer.layers[0].name = new_fov['fov_name']
            viewer.layers[1].data = mask

            for i, point in enumerate(points):
                viewer.layers[i+2].data = point['coords']
            
            viewer.status = new_fov.fov_name

if __name__ == '__main__':
    args = _parse_args()

    # Get the Experiment
    experiment_path = args.exp
    exp = Experiment.from_json(experiment_path)

    fov_df = pd.read_csv(args.fovs)

    view_results(fov_df, exp)