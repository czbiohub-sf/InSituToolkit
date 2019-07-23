import warnings
from typing import List, Optional

import numpy as np
from starfish import ImageStack

from ._image_database import ImageDatabase

def get_numpy_stack(db_credentials: str, image_ids: str, channels, pos: int = 0, time: int = 0):
    """
    Downloads an image stack from the imaging database and returns it as a numpy ndarray.

    Parameters
    ----------
    db_credentials : str
        Path to the database credentials file
    image_ids : List[str]
        A list of the image ids in the order of the 
    channels : Optional[]
        A list of the channels to be downloaded in the index order.
    pos : int
        Index of the position to download. The default value is 0.
    time : int
        Index of the time point to download. The default value is 0.

    returns
    ----------
    im_stack : np.ndarray
        image stack with order (r, c, z, y, x)

    """
    db = ImageDatabase(db_credentials)

    n_rounds = len(image_ids)
    n_channels = len(channels)

    im_stack = np.zeros((n_rounds, n_channels, n_slices, im_width, im_height), dtype='uint16')
    for r, im in enumerate(image_id):
        for c, chan in enumerate(channels):
            im_stack[r, c, ...] = db.getStack(im, channel=chan, pos_idx=pos, time_idx=time)

    return im_stack

def get_image_stack(db_credentials: str, image_id: str, channels, pos: int = 0, time: int = 0):
    """
    Downloads an image stack from the imaging database and returns it as a starfish ImageStack.

    Parameters
    ----------
    db_credentials : str
        Path to the database credentials file
    image_ids : List[str]
        A list of the image ids in the order of the 
    channels : Optional[]
        A list of the channels to be downloaded in the index order.
    pos : int
        Index of the position to download. The default value is 0.
    time : int
        Index of the time point to download. The default value is 0.

    returns
    ----------
    im_stack : ImageStack
        image stack
    """
    im_stack = get_numpy_stack(db_credentials, image_id, channels, pos, time)

    # Suppress the loss of precision warning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stack = ImageStack.from_numpy(im_stack)

    return stack