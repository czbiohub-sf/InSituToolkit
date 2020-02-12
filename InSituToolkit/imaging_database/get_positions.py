import imaging_db.database.db_operations as db_ops
import imaging_db.utils.db_utils as db_utils


def get_positions(db_credentials: str, dataset_serial: str):
    """
    Queries the database for a given dataset serial number and returns list of available positions

    Parameters
    ----------
    db_credentials: str
        Absolute url to location of .json credentials
    dataset_serial: str
        dataset_serial field of a dataset in the database

    Returns
    -------
    List[int] of positions for a given experiment
    """
    credentials_str = db_utils.get_connection_str(db_credentials)

    with db_ops.session_scope(credentials_str) as session:
        frames = session.query(db_ops.Frames) \
            .join(db_ops.FramesGlobal) \
            .join(db_ops.DataSet) \
            .filter(db_ops.DataSet.dataset_serial == dataset_serial)
    positions = set()
    for f in frames:
        positions.add(f.pos_idx)
    return list(positions)