from os import path
import sys
import subprocess
from typing import List

from ._make_experiment_csv import make_experiment_csv


def write_experiment(
                     db_credentials:str, output_folder:str, image_ids,
                     spot_channels:List[str], stain_channels:List[str] = None,
                     nuc_channels:List[str] = None, metadata_format:str = 'micromanager',
                     positions:List[int] = [0], time:int=0,
                     data_path:str = '/Volumes/imaging/czbiohub-imaging/'
                    ):
    """
    Writes the spacetx format experiment files for analysis in starfish

    Parameters
    ----------
    db_credentials : str
        Path to the database credentials file
    output_folder : str
        Path to save the experiment files to
    image_ids : List[str]
        List of the image IDs to include in the data set. Each image id will be a "round" in starfish.
    spot_channels : List[str]
        A list of the channels containing the spots
    stain_channels : List[str]
        A list of the channels containing any auxillary stains
        (e.g., GFP or membrane stain for segmentation)
    nuc_channels : List[str]
        A list of the channels containing any nuclear stains (e.g., DAPI)
    metadata_format : str
        Format for the image metadata on imagingDB. For micromanager, set to 'micromanager'.
        Default value is 'micromanager'
    positions : int
        Index of the position to download. The default value is 0.
    time : int
        Index of the time point to download. The default value is 0.
    data_path : str
        Path to the image store volume
    """

    spots_file_path = path.join(output_folder, 'spots.csv')
    tile_width, tile_height = make_experiment_csv(
                                                  db_credentials, spots_file_path, image_ids,
                                                  spot_channels, metadata_format, positions, time,
                                                  data_path
    )
    csv_args = 'primary ' + spots_file_path

    if stain_channels is not None:
        stain_file_path = path.join(output_folder, 'stain.csv')
        _, _ = make_experiment_csv(
                            db_credentials, stain_file_path, image_ids,
                            stain_channels, metadata_format, positions, time
        )

        csv_args += ' --csv-file stain ' + stain_file_path

    if nuc_channels is not None:
        stain_file_path = path.join(output_folder, 'nuclei.csv')
        _, _ = make_experiment_csv(
                            db_credentials, stain_file_path, image_ids,
                            nuc_channels, metadata_format, positions, time
        )

        csv_args += ' --csv-file nuclei ' + stain_file_path

    cmd = 'spacetx_biohub_writer ' + '--tile-width ' + str(tile_width) + ' ' + \
            '--tile-height ' + str(tile_height) + ' ' + \
            '--s3-prefix ' + data_path + ' ' + \
            '--output-dir ' + output_folder + ' ' + \
            '--csv-file ' + csv_args

    subprocess.call(cmd, shell=True)