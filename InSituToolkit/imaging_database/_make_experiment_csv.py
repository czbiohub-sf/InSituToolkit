import os
import hashlib
from typing import List, Union

import boto3
import numpy as np
import pandas as pd
import imaging_db.filestorage.s3_storage as s3_storage
import imaging_db.database.db_operations as db_ops
import imaging_db.utils.db_utils as db_utils

from ._constants import metadata_keys


def make_experiment_csv(
                        db_credentials:str, csv_file:str, image_ids:List[str], channels:List[str],
                        metadata_format:str = 'micromanager', positions:int = [0], time:int=0,
                        z_slices:Union[None, List[int]] = None,
                        data_path:str = '/Volumes/imaging/czbiohub-imaging'
                        ):
    """
    Creates a CSV file mapping imagingDB frames to indices in an ImageStack
    for usage with the spacetx format writer.

    Parameters
    ----------
    db_credentials : str
        Path to the database credentials file
    file_path : str
        file_path of the resulting CSV file 
    metadata_format : str
        Format for the image metadata on imagingDB. For micromanager, set to 'micromanager'.
        Default value is 'micromanager'
    image_ids : List[str]
        A list of the image ids in the order of the 
    channels : Optional[]
        A list of the channels to be downloaded in the index order.
    positions : int
        Index of the position to download. The default value is 0.
    time : int
        Index of the time point to download. The default value is 0.
    z_slices : Union[None, List[int]]
        Array of z slices indices to include. Can use a 1D array to use same z slices for each round.
        Can use a 2D array where the first dimension is the round index to use different z slice indices
        for each round. Use None if grabbing all z slices. Default value is None
    data_path : str
        Path to the image store volume
    """
    meta_keys = metadata_keys[metadata_format.lower()]

    fov = []
    rnd = []
    channel = []
    z = []
    file_path = []
    #sha = []
    xc_min = []
    xc_max = []
    yc_min = []
    yc_max = []
    zc_min = []
    zc_max = []
    tile_width = []
    tile_height = []

    credentials_str = db_utils.get_connection_str(db_credentials)

    with db_ops.session_scope(credentials_str) as session:
        for r, im_id in enumerate(image_ids):
            for fov_idx, p in enumerate(positions):
                for chan_idx, c in enumerate(channels):
                    frames = session.query(db_ops.Frames) \
                        .join(db_ops.FramesGlobal) \
                        .join(db_ops.DataSet) \
                        .filter(db_ops.DataSet.dataset_serial == im_id) \
                        .filter(db_ops.Frames.pos_idx == p) \
                        .filter(db_ops.Frames.channel_name == c) \
                        .filter(db_ops.Frames.time_idx == time)

                    # if getting only selected z slices, filter
                    if np.ndim(z_slices) == 1 or np.ndim(z_slices) == 2:
                        if np.ndim(z_slices) == 1:
                            curr_zslices = z_slices
                        else:
                            curr_zslices = z_slices[r]
                        frames = frames.filter(db_ops.Frames.slice_idx.in_(curr_zslices))

                        for z_idx, z_slice in enumerate(curr_zslices):
                            z_frames = frames.filter(db_ops.Frames.slice_idx == z_slice)

                            for frame in z_frames:
                                # Determine image info
                                pixel_size = frame.metadata_json[meta_keys['key']][meta_keys['pixel_size']]
                                im_width = frame.frames_global.im_width
                                im_height = frame.frames_global.im_height

                                # Add frame indices
                                fov.append(fov_idx)
                                rnd.append(r)
                                channel.append(chan_idx)
                                z.append(z_idx)
                                # Clean any windows file path seps before adding path
                                fp = os.path.join(frame.frames_global.storage_dir, frame.file_name)
                                clean_fp = os.path.join(*fp.split('\\'))
                                file_path.append(clean_fp)
                                xc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['xpos_um']])
                                xc_max.append(xc_min[-1] + im_width * pixel_size)
                                yc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['ypos_um']])
                                yc_max.append(yc_min[-1] + im_height * pixel_size)
                                zc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['zpos_um']])
                                zc_max.append(frame.metadata_json[meta_keys['key']][meta_keys['zpos_um']])
                                tile_width.append(im_width)
                                tile_height.append(im_height)

                    # otherwise get all z slices
                    elif z_slices is None:
                        for frame in frames:
                            # Determine image info
                            pixel_size = frame.metadata_json[meta_keys['key']][meta_keys['pixel_size']]
                            im_width = frame.frames_global.im_width
                            im_height = frame.frames_global.im_height

                            # Add frame indices
                            fov.append(fov_idx)
                            rnd.append(r)
                            channel.append(chan_idx)
                            z.append(frame.slice_idx)
                            # Clean any windows file path seps before adding path
                            fp = os.path.join(frame.frames_global.storage_dir, frame.file_name)
                            clean_fp = os.path.join(*fp.split('\\'))
                            file_path.append(clean_fp)
                            xc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['xpos_um']])
                            xc_max.append(xc_min[-1] + im_width * pixel_size)
                            yc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['ypos_um']])
                            yc_max.append(yc_min[-1] + im_height * pixel_size)
                            zc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['zpos_um']])
                            zc_max.append(frame.metadata_json[meta_keys['key']][meta_keys['zpos_um']])
                            tile_width.append(im_width)
                            tile_height.append(im_height)

    sha = _calc_checksums(file_path, data_path)
                    
    data = [fov, rnd, channel, z, file_path, sha, xc_min, xc_max, yc_min, yc_max, zc_min, zc_max, tile_width, tile_height]
    columns = [
                'fov','round', 'ch', 'zplane', 'path','sha256', 'xc_min',
                'xc_max', 'yc_min', 'yc_max', 'zc_min', 'zc_max', 'tile_width', 'tile_height'
              ]
    im_df = pd.DataFrame(dict(zip(columns, data)))
    im_df.to_csv(csv_file)

    return im_width, im_height

def _calc_checksums(file_names, data_path):
    checksums = []

    for file in file_names:
        # We need to replace any windows file separators with the proper separator
        cleaned_filename = os.path.join(*file.split('\\'))
        filename = os.path.join(data_path, cleaned_filename)
        with open(filename,"rb") as f:
            bytes = f.read() # read entire file as bytes
            readable_hash = hashlib.sha256(bytes).hexdigest();

            checksums.append(readable_hash)

    return checksums
