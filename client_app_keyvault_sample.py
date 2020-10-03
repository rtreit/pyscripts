import os
import requests, json
import sys, getopt

keyvault_secret=os.environ['KEYVAULT_SECRET'],

def get_keyvault_access_token():
    url = "https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/oauth2/token"
    payload = {
        "grant_type":"client_credentials",
        "client_id":"5f6354ba-13ae-413f-9fcb-9deb5eeed1c7",
        "client_secret": keyvault_secret,
        "resource":"https://vault.azure.net"
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    return response.json()["access_token"]

def get_secret_from_keyvault(
    secret_name,
    vault="",  # <vault_name>.vault.azure.net goes here
    tenant="",  # tenant for Azure subscription
):

    token = get_keyvault_access_token()

    headers = {"authorization": f"bearer {token}"}
    url = f"https://{vault}/secrets/{secret_name}/?api-version=7.0"
    r = requests.get(url, headers=headers)
    return r.json()["value"]

def main(secret):
    secret = get_secret_from_keyvault(secret)
    print(secret)


if __name__ == "__main__":
    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <secret to retrieve>")
    main(arg)
