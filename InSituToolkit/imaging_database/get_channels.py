
from imaging_db.database.db_operations import DatabaseOperations
import imaging_db.database.db_operations as db_ops
import imaging_db.utils.db_utils as db_utils

def get_channels(db_credentials: str, dataset_id: str):
    """
    Queries the database for a dataset id and returns a dict of channel assignments

    Parameters
    ----------
    db_credentials: str
        Absolute url to location of .json credentials
    dataset_serial: str
        dataset_serial field of a dataset in the database

    Returns
    -------
    Dict of (channel_idx:channel_name) pairs
    """
    dbops = DatabaseOperations(dataset_id)
    credentials_str = db_utils.get_connection_str(db_credentials)
    with db_ops.session_scope(credentials_str) as session:
        _, frames_meta = dbops.get_frames_meta(session)

    df = frames_meta[['channel_name', 'channel_idx']].drop_duplicates()
    channels = {}
    for idx, row in df.iterrows():
        channels[row['channel_idx']] = row['channel_name']
    return channels
