from google.cloud import bigquery


def get_client(project: str | None = None) -> bigquery.Client:
    """Return a BigQuery client.

    If *project* is None the client uses the default project from
    GOOGLE_CLOUD_PROJECT or gcloud config.
    """
    return bigquery.Client(project=project)
