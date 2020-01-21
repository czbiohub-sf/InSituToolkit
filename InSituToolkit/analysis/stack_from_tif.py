import numpy as np
from skimage import io, img_as_uint
from starfish import ImageStack
import string

def stack_from_tif(file_name: string ) -> ImageStack:
    """
    Returns an ImageStack object from a tif file
    Parameters
    ----------
    file_name: string
        Location of a tif file

    Returns
    -------
    ImageStack
    """
    image = io.imread(file_name)
    img_num = np.array(image, dtype=np.uint16)
    img_dim = len(np.shape(img_num))
    [img_ch, img_y, img_x] = [1, 1, 1]

    # Treat stacks of tiff's as multiple channels
    if img_dim == 3:
        [img_ch, img_y, img_x] = np.shape(img_num)

    if img_dim == 2:
        [img_y, img_x] = np.shape(img_num)
        img_ch  = 1

    if not ((len(np.shape(img_num)) == 2) or (len(np.shape(img_num)) == 3)):
        raise Exception('Dimensionality error: images must be 2D or 2D stacks')

    stack = np.empty([1, img_ch, 1, img_y, img_x])

    if img_dim == 2:
        stack[0, 0, 0, :, :] = img_num[:, :]

    if img_dim == 3:
        stack[0, :, 0, :, :] = img_num[:, :, :]

    image_stack = ImageStack.from_numpy(stack)
    return image_stack
