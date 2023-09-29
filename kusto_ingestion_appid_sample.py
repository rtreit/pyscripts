import os
import pandas as pd
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.ingest import (
    IngestionProperties,
    QueuedIngestClient,
    KustoStreamingIngestClient,
)
from azure.kusto.data.data_format import DataFormat

client_id = os.environ["APP_ID"]
client_secret = os.environ["APP_SECRET"]
authority_id = os.environ["AZURE_TENANT_ID"]
cluster = "" # enter your cluster name here
database = "" # enter your database here

def query_kusto(query_cluster, query_database, query):
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
        query_cluster, client_id, client_secret, authority_id
    )
    with KustoClient(kcsb) as client:
        response = client.execute(query_database, query)
        columns = [col.column_name for col in response.primary_results[0].columns]
        data = [row for row in response.primary_results[0]]
        df = pd.DataFrame(data, columns=columns)
        return df


def ingest_kusto_queued(df, ingest_cluster, ingest_database, ingest_table):
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
        ingest_cluster, client_id, client_secret, authority_id
    )
    client = QueuedIngestClient(kcsb)
    ingestion_properties = IngestionProperties(
        database=ingest_database, table=ingest_table
    )
    ingestion = client.ingest_from_dataframe(
        df, ingestion_properties=ingestion_properties
    )
    return ingestion.status


def ingest_kusto_streaming(df, ingest_cluster, ingest_database, ingest_table):
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(
        ingest_cluster, client_id, client_secret, authority_id
    )
    client = KustoStreamingIngestClient(kcsb)
    ingestion_properties = IngestionProperties(
        database=ingest_database, table=ingest_table, data_format=DataFormat.CSV
    )
    ingestion = client.ingest_from_dataframe(
        df, ingestion_properties=ingestion_properties
    )
    return ingestion.status


if __name__ == "__main__":
    query_cluster = f"https://{cluster}.kusto.windows.net"
    query_database = f"lshash"
    query = f"lshash_metadata | sample 1000"
    df = query_kusto(query_cluster, query_database, query)
    print(df)

    ingest_cluster = f"https://ingest-{cluster}.kusto.windows.net"
    stream_cluster = f"https://{cluster}.kusto.windows.net"
    ingest_database = f"{database}"
    queued_ingest_table = "DebugQueued"
    streaming_ingest_table = "DebugStreaming"
    queued_ingestion_status = ingest_kusto_queued(
        df, ingest_cluster, ingest_database, queued_ingest_table
    )
    print(queued_ingestion_status)
    streaming_ingestion_status = ingest_kusto_streaming(
        df, stream_cluster, ingest_database, streaming_ingest_table
    )
    print(queued_ingestion_status)
