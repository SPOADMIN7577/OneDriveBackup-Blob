import requests
from core.blob import upload_if_not_exists

def run_copy(files, container, base_dir, headers):
    copied = []

    for item in files:
        relative = (
            item["parentReference"]["path"]
            .replace("/drive/root:", "")
            .lstrip("/")
        )
        blob_path = f"{base_dir}/{relative}/{item['name']}".strip("/")

        meta = {
            "lastmodified": item["lastModifiedDateTime"],
            "onedrive_fileid": item["id"],
            "filesize": str(item["size"])
        }

        r = requests.get(item["@microsoft.graph.downloadUrl"], headers=headers, stream=True)

        if upload_if_not_exists(container, blob_path, r.raw, meta):
            copied.append(blob_path)

    return copied
