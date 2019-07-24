from os import path
import sys
import subprocess

from ._make_experiment_csv import make_experiment_csv

def write_experiment(
                     db_credentials:str, output_folder:str, image_ids, channels,
                     metadata_format:str = 'micromanager', positions:int = [0], time:int=0
                    ):

    file_path = path.join(output_folder, 'database.csv')
    tile_width, tile_height = make_experiment_csv(
                                                  db_credentials, file_path, image_ids,
                                                  channels, metadata_format, positions, time
                                                 ) 
    cmd = 'spacetx_biohub_writer ' + '--tile-width ' + str(tile_width) + ' ' + \
            '--tile-height ' + str(tile_height) + ' ' + \
            '--s3-prefix ' + 's3://czbiohub-imaging/ ' + \
            '--output-dir ' + output_folder + ' ' + \
            '--csv-file ' + 'primary ' + file_path 

    subprocess.call(cmd, shell=True)