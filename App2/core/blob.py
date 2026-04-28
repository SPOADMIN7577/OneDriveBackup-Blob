from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError


def get_container(storage_account: str, storage_key: str, container_name: str):
    """
    Returns a ContainerClient for the given storage account.
    """
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={storage_account};"
        f"AccountKey={storage_key};"
        f"EndpointSuffix=core.windows.net"
    )

    service_client = BlobServiceClient.from_connection_string(connection_string)
    return service_client.get_container_client(container_name)


def upload_if_not_exists(
    container_client,
    blob_path: str,
    data_stream,
    metadata: dict
) -> bool:
    """
    Uploads a blob only if it does NOT already exist.
    Returns True if uploaded, False if skipped.
    """
    blob_client = container_client.get_blob_client(blob_path)

    try:
        # If this succeeds, blob already exists
        blob_client.get_blob_properties()
        return False
    except ResourceNotFoundError:
        blob_client.upload_blob(
            data=data_stream,
            overwrite=False,
            metadata=metadata
        )
        return True