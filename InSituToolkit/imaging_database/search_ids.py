import imaging_db.database.db_operations as db_ops
import imaging_db.utils.db_utils as db_utils


def search_ids(db_credentials: str, string: str):
    """
    Retrieves all the datasets in database whose id's contain a specified string
    Parameters
    ----------
    db_credentials: str
        User credentials for the current session
    string: str
        string to match to dataset id's

    Returns
    -------
    List[string] - list of dataset id's that contain the specified string
    """
    credentials_str = db_utils.get_connection_str(db_credentials)
    with db_ops.session_scope(credentials_str) as session:
        frames = session.query(db_ops.DataSet)

    set_of_ids = list()
    for f in frames:
        name = f.dataset_serial
        if string in name:
            set_of_ids.append(name)
    return list(set_of_ids)