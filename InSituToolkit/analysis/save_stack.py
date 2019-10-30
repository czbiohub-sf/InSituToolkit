import numpy as np
from skimage import io, img_as_uint
from starfish import ImageStack

def save_stack(im_stack:ImageStack, file_name:str):
    """
    Save a starfish ImageStack to disk

    Parameters
    ----------
    im_stack : ImageStack
        The starfish ImageStack to be saved

    file_name : str
        Name for the image file. The extension will set the format
        as defined my skimage.io. Images with be 16 bit uint.

    """
    im_array = np.squeeze(im_stack.xarray.data)
    io.imsave(file_name, img_as_uint(im_array))
