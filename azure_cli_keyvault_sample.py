import requests
import sys, getopt
from azure.common.credentials import get_cli_profile


def get_secret_from_key_vault(
    secret_name,
    vault="",  # vault name goes here
    tenant="",  # tenant for Azure subscription
):
    profile = get_cli_profile()

    cli_token = profile.get_access_token_for_resource(
        resource="https://vault.azure.net",
        username=profile.get_current_account_user(),
        tenant=tenant,
    )
    headers = {"authorization": f"bearer {cli_token}"}
    url = f"https://{vault}.vault.azure.net/secrets/{secret_name}/?api-version=7.0"
    r = requests.get(url, headers=headers)
    return r.json()["value"]


def main(secret):
    secret = get_secret_from_key_vault(secret)
    print(secret)


if __name__ == "__main__":
    try:
        arg = sys.argv[1]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <secret to retrieve>")
    main(arg)
