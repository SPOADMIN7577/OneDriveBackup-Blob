import requests
from collections import deque

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def discover_files(headers, user, path=None):
    queue = deque()
    files = []

    if path:
        queue.append(f"{GRAPH_BASE}/users/{user}/drive/root:/{path}:/children")
    else:
        queue.append(f"{GRAPH_BASE}/users/{user}/drive/root/children")

    while queue:
        url = queue.popleft()
        data = requests.get(url, headers=headers).json()

        for item in data.get("value", []):
            if "folder" in item:
                queue.append(
                    f"{GRAPH_BASE}/users/{user}/drive/items/{item['id']}/children"
                )
            else:
                files.append(item)

        if "@odata.nextLink" in data:
            queue.append(data["@odata.nextLink"])

    return files
