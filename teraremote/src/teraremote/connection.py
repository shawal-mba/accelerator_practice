import teradatasql


def get_connection(host: str, user: str, password: str) -> teradatasql.TeradataConnection:
    """Return a Teradata connection with encryption enabled."""
    return teradatasql.connect(
        None,
        host=host,
        user=user,
        password=password,
        encryptdata=True,
    )
