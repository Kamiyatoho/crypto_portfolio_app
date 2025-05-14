from datetime import datetime, timezone


def to_timestamp(dt: datetime) -> int:
    """
    Convert a datetime object to a Unix timestamp in milliseconds.

    Parameters:
    dt (datetime): A datetime object. Should be timezone-aware or naive in local time.

    Returns:
    int: Timestamp in milliseconds since the Unix epoch.
    """
    # Use UTC if timezone-aware, else treat as local
    if dt.tzinfo is None:
        # naive datetime, assume local
        ts = dt.timestamp()
    else:
        # convert to UTC
        ts = dt.astimezone(timezone.utc).timestamp()
    return int(ts * 1000)


def from_timestamp(ts: int) -> datetime:
    """
    Convert a Unix timestamp in milliseconds to a datetime object in local time.

    Parameters:
    ts (int): Timestamp in milliseconds since the Unix epoch.

    Returns:
    datetime: A naive datetime object in local time.
    """
    # Convert milliseconds to seconds
    seconds = ts / 1000
    # Create datetime
    return datetime.fromtimestamp(seconds)