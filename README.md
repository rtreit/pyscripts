# pyscripts
Python scripts I find useful in my everyday life.

## Script Descriptions

- **azure_cli_keyvault_sample.py**: Retrieves secrets from Azure Key Vault using Azure CLI credentials.
- **azure_cli_kusto_sample.py**: Queries Azure Data Explorer (Kusto) using Azure CLI credentials and prints results as a table.
- **chesscom_downloader.py**: Downloads chess.com games as PGN via the archives API. Defaults to incremental mode (only games newer than your most recent downloaded game) and supports `--fetch-all` to force a full download. Includes duplicate detection for safe re-runs.
- **client_app_keyvault_sample.py**: Retrieves secrets from Azure Key Vault using a client application's credentials (client ID/secret).
- **comment_replacer.py**: Recursively searches for and removes specific TODO comments from C# files in a directory.
- **directory_hasher.py**: Recursively computes SHA256 hashes for files in a directory, outputs details and deduplicated hashes.
- **kusto_ingestion_appid_sample.py**: Demonstrates querying and ingesting data into Azure Data Explorer (Kusto) using application credentials.
- **list_to_code.py**: Reads a list of values from a file and writes them as C# Guid.Parse statements to an output file.
- **python_examples.py**: Contains miscellaneous Python code examples, such as finding keys in nested dictionaries.
