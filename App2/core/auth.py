import msal

def get_app(tenant_id, client_id, client_secret):
    return msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret
    )

def get_graph_headers(app):
    token = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" not in token:
        raise Exception(token)
    return {"Authorization": f"Bearer {token['access_token']}"}