from os import path
import sys
import subprocess

from ._make_experiment_csv import make_experiment_csv

DATA_PATH = '/Volumes/imaging/czbiohub-imaging/'

def write_experiment(
                     db_credentials:str, output_folder:str, image_ids, spot_channels, stain_channels=None, nuc_channels=None,
                     metadata_format:str = 'micromanager', positions:int = [0], time:int=0
                    ):

    spots_file_path = path.join(output_folder, 'spots.csv')
    tile_width, tile_height = make_experiment_csv(
                                                  db_credentials, spots_file_path, image_ids,
                                                  spot_channels, metadata_format, positions, time
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
            '--s3-prefix ' + DATA_PATH + ' ' + \
            '--output-dir ' + output_folder + ' ' + \
            '--csv-file ' + csv_args

    subprocess.call(cmd, shell=True)