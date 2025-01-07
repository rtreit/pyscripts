# get Azure CLI login refresh token (Fiddler, etc) and exchange it for a resource-scoped access token for that user

import os
import requests
import pandas as pd
from typing import Tuple, Optional

def exchange_refresh_token_for_access_token(
    refresh_token: str,
    client_id: str,
    tenant_id: str,
    resource: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Exchanges an Azure CLI login refresh token for a Kusto-scoped access token
    (and possibly a new Kusto refresh token).

    :param refresh_token: The original refresh token (e.g., for management.azure.com).
    :param client_id: Azure AD application (client) ID for Azure CLI.
    :param tenant_id: Azure AD tenant ID.
    :param resource: URL of the resource (e.g. https://<cluster>.kusto.windows.net, https://storage.azure.com, etc).
    :return: A tuple (access_token, new_refresh_token).
             If any token is not returned by Azure AD, it will be None.
    """
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token,
        "scope": f"{resource}/.default"  # Request resource-specific token
    }

    response = requests.post(token_url, headers=headers, data=data)
    resp_json = response.json()

    if response.status_code == 200:
        return (
            resp_json.get("access_token"),
            resp_json.get("refresh_token")
        )
    else:
        print(f"Failed to exchange refresh token. Error: {resp_json.get('error_description')}")
        return (None, None)

def main():
    refresh_token = os.getenv("REFRESH_TOKEN") 
    client_id     = os.getenv("REFRESH_CLIENT_ID") 
    tenant_id     = os.getenv("TENANT_ID")  

    resource = f"https://storage.azure.com" 

    access_token, new_refresh_token = exchange_refresh_token_for_access_token(
        refresh_token=refresh_token,
        client_id=client_id,
        tenant_id=tenant_id,
        resource=resource
    )

    if not access_token:
        print("Failed to get access token.")
        return

    print("Access Token:", access_token)
    if new_refresh_token:
        print("\nRefresh Token:", new_refresh_token)

if __name__ == "__main__":
    main()
