import os

from ._constants import metadata_keys

def make_experiment_csv(
                        db_credentials:str, file_path:str, metadata_format:str = 'micromanager',
                        image_ids, channels, positions:int = 0, time:int=0
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
    """

    meta_keys = metadata_keys[metadata_format.lower()]

    fov = []
    rnd = []
    channel = []
    z = []
    file_path = []
    sha = []
    xc_min = []
    xc_max = []
    yc_min = []
    yc_max = []
    zc = []
    with db_session.session_scope(db_credentials) as session:
        for r, im_id in enumerate(image_ids):
            for fov_idx, p in enumerate(positions):
                for chan_idx, c in enumerate(channels):
                    frames = session.query(db_session.Frames) \
                        .join(db_session.FramesGlobal) \
                        .join(db_session.DataSet) \
                        .filter(db_session.DataSet.dataset_serial == im_id) \
                        .filter(db_session.Frames.pos_idx == p) \
                        .filter(db_session.Frames.channel_name == c)
                        .filter(db_session.Frames.time_idx == time)

                    for frame in frames:
                        # Determine
                        pixel_size = frame.metadata_json[meta_keys['key']][meta_keys['pixel_size']
                        im_width = frame.first().frames_global.im_width
                        im_height = frame.first().frames_global.im_height

                        # Add frame indices
                        fov.append(fov_idx)
                        rnd.append(r)
                        channel.append(chan_idx)
                        z.append(frame.slice_idx)
                        file_path.append(os.path.join(frame.frames_global.s3_dir, frame.file_name))
                        sha.append(frame.sha256)
                        xc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['xpos_um']
                        xc_max.append(xc_min + im_width * pixel_size)
                        yc_min.append(frame.metadata_json[meta_keys['key']][meta_keys['ypos_um']])
                        yc_max.append(yc_min + im_height * pixel_size)
                        zc.append(frame.metadata_json[meta_keys['key']][meta_keys['zpos_um']])
                    
    indices = [fov, rnd, channel, z, file_path, sha, xc_min, xc_max, yc_min, yc_max, zc]
    im_df = pd.DataFrame(data=indices,
                         columns=['fov','rnd', 'channel', 'zplane', 'file_path',
                                 'sha256', 'xc_min', 'xc_max', 'yc_min', 'yc_max', 'zc']
                        )
    im_df.to_csv(file_path)
