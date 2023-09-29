import sys
import pandas as pd
from io import StringIO
import requests
from azure.common.credentials import get_cli_profile
import json
from tabulate import tabulate


profile = get_cli_profile()


def query_kusto_rest(
    query,
    kusto_cluster="",  # TODO: kusto cluster (e.g. mycluster.kusto.windows.net)
    kusto_database="",  # TODO: kusto database goes here
    kusto_tenant="",  # TODO: kusto tenant goes here
):
    cli_token = profile.get_access_token_for_resource(
        resource=f"https://{kusto_cluster}",
        username=profile.get_current_account_user(),
        tenant=kusto_tenant,
    )
    headers = {
        "Authorization": f"bearer {cli_token}",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Host": f"{kusto_cluster}",
    }

    params = {"db": f"{kusto_database}", "csl": f"{query}"}

    url = f"https://{kusto_cluster}/v1/rest/query"
    r = requests.get(url, headers=headers, params=params)
    result = r.json()
    rows = result["Tables"][0]["Rows"]
    columns = result["Tables"][0]["Columns"]
    columns[0]["ColumnName"]
    column_names = []
    for index in range(0, len(columns)):
        column_names.append(columns[index]["ColumnName"])
    table = json.dumps(rows)
    df = pd.read_json(StringIO(json.dumps(rows)))
    df.columns = column_names
    df = df.infer_objects()
    return df


def main(cluster, db, tenant, query):
    df = query_kusto_rest(
        kusto_cluster=cluster, kusto_database=db, kusto_tenant=tenant, query=query
    )
    print(tabulate(df, headers="keys", tablefmt="simple", showindex="never",))


if __name__ == "__main__":
    try:
        cluster = sys.argv[1]
        db = sys.argv[2]
        tenant = sys.argv[3]
        query = sys.argv[4]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} cluster db tenant query")
    main(cluster, db, tenant, query)
