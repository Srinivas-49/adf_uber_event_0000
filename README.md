# Uber Event Streaming — Azure Data Factory ingestion

[![Azure Data Factory](https://img.shields.io/badge/Azure-Data%20Factory-0078D4)](https://azure.microsoft.com/products/data-factory)
[![Azure Data Lake Storage](https://img.shields.io/badge/Storage-ADLS%20Gen2-0078D4)](https://learn.microsoft.com/azure/storage/blobs/data-lake-storage-introduction)

> **Part 1 of a two-repository project.** This repository contains the **Azure Data Factory (ADF) batch/reference-data ingestion** portion of **Uber Event Streaming**. The companion [Databricks repository](https://github.com/Srinivas-49/uber_-streaming_project_azure) contains Event Hubs consumption, streaming transformations, medallion layers, and analytics.

## Project overview

This project combines a **batch/reference-data path** with a **ride-event streaming path**:

```text
Batch / reference-data path (this repository)
GitHub-hosted JSON files
      |
      v
Azure Data Factory: HTTP_to_ADLS
  Lookup1 -> foreachjson -> Copy data1 (HTTP GET)
      |
      v
ADLS Gen2: raw/igestion/<file>.json
      |
      v
Databricks: Bronze lookup tables
      |
      +------------------------------+
                                     |
Streaming rides path (companion repo)|
Azure Event Hubs (Kafka endpoint)    |
      |                              |
      v                              |
Databricks Bronze (rides_raw)        |
      |                              |
      v                              |
Bronze (stg_rides) ------------------+
      |
      v
Silver (silver_obt: enriched rides)
      |
      v
Gold (dimensions, fact, analytics)
```

The repo contains the ADF definitions only; the Event Hubs producer, deployed Azure resources and Databricks pipeline/job configuration are **not** included here.

## What the ADF pipeline does

[HTTP_to_ADLS.json](adf_uber_event_0000/pipeline/HTTP_to_ADLS.json) defines:

1. **`Lookup1`** reads a JSON file list from the `lookup_json_file` dataset in ADLS, with `firstRowOnly: false`.
2. **`foreachjson`** loops over `@activity('Lookup1').output.value`.
3. **`Copy data1`** uses an HTTP JSON source (`dataset_github`) and writes to the parameterized ADLS JSON sink (`Json3`). Both source and sink receive `@concat(item().file, '.json')`.

An expected lookup-row shape is:

```json
[
  {"file": "map_cities"},
  {"file": "map_vehicle_types"},
  {"file": "map_payment_methods"}
]
```

The lookup dataset currently targets `raw/files_array (1).json`; this example illustrates the required rows, not the contents of that uncommitted storage file.

### Datasets and connections

| ADF artifact | Role |
| --- | --- |
| `lookup_json_file` | JSON input listing filenames; `raw/files_array (1).json` |
| `dataset_github` | Parameterized HTTP source for `<file>.json` |
| `Json3` | Active parameterized ADLS destination: `raw/igestion/<file>.json` |
| `Json1` | Additional HTTP dataset, not referenced by the current pipeline |
| `Json2` | Additional ADLS dataset pointing at `raw/ingestion/`, not referenced by the current pipeline |
| `ls_github_adf` | Anonymous HTTP linked service to `raw.githubusercontent.com` |
| `ls_adls_uber_00000` | ADLS linked service used by the lookup dataset and active sink |
| `ls_adls_adf_uber_0000` | Separate ADLS linked service used by `Json2` |

**Important:** The active sink folder is spelled **`igestion`** (not `ingestion`). This matches the path currently read by the Databricks Bronze notebook. Do not rename it in only one system; change ADF and Databricks together if you standardize the spelling.

### Source data

The current HTTP dataset constructs a path under:

```text
https://raw.githubusercontent.com/anshlambagit/Uber_Data_Engineer_Project/refs/heads/main/Data/<file>.json
```

This is an upstream dataset referenced by the ADF JSON, **not** this project's Databricks repository. Confirm the files are publicly reachable and that the HTTP linked service and dataset resolve the URL correctly before executing.

The Databricks exploration notebook references `bulk_rides` plus lookup entities such as `map_cities`, `map_cancellation_reasons`, `map_payment_methods`, `map_ride_statuses`, `map_vehicle_makes`, and `map_vehicle_types`. The exact set copied depends on the external lookup file.

## Repository structure

```text
README.md
adf_uber_event_0000/
├── factory/
│   └── adfuberevent0000.json
├── pipeline/
│   └── HTTP_to_ADLS.json
├── dataset/
│   ├── dataset_github.json
│   ├── lookup_json_file.json
│   ├── Json1.json
│   ├── Json2.json
│   └── Json3.json
├── linkedService/
│   ├── ls_github_adf.json
│   ├── ls_adls_uber_00000.json
│   └── ls_adls_adf_uber_0000.json
└── publish_config.json
```

## Setup and run

**Prerequisites:** an Azure subscription, an ADF instance, an ADLS Gen2 account/container, permissions to read/write the relevant ADLS paths, and accessible upstream JSON files. The Databricks stage is configured separately.

1. Create or select the Azure Data Factory and ADLS Gen2 resources.
2. Import or connect the JSON artifacts under `adf_uber_event_0000/` through ADF Git integration or an appropriate deployment workflow. These files are definitions, not a one-click infrastructure deployment.
3. Review the linked services and replace environment-specific storage endpoints and credentials with your own secure configuration (prefer managed identity/Key Vault).
4. Ensure the `raw` filesystem contains a valid `files_array (1).json` lookup file, with one `file` value per JSON object.
5. Check the HTTP dataset path, dataset parameters and linked-service connectivity.
6. In ADF Studio, **Validate**, **Debug**, then **Publish** and **Trigger** `HTTP_to_ADLS`.
7. In **Monitor**, inspect `Lookup1`, `foreachjson` and each `Copy data1` execution. Verify files appear at `raw/igestion/<file>.json`.
8. Continue with the [Databricks transformation repository](https://github.com/Srinivas-49/uber_-streaming_project_azure).

## Operational checks

- **Lookup returned no rows:** verify `raw/files_array (1).json`, the expected JSON array/objects, and ADLS permissions.
- **HTTP 404:** verify each `<file>.json` path, branch and accessibility in the upstream public repository.
- **Copy failed:** check source/sink linked services, credentials, `raw` filesystem and parameterized filenames.
- **Databricks cannot find JSON:** verify the exact `igestion` spelling and the ADLS account used by both sides.

## Security and scope

Linked-service exports include environment-specific endpoints and encrypted credential metadata. Avoid committing actual storage keys, Event Hubs connection strings, tokens or customer data. Use managed identities and secret management in deployed environments.

This repo documents **batch JSON ingestion**; it does **not** itself implement the live ride-event producer or prove end-to-end streaming deployment. See the [companion Databricks README](https://github.com/Srinivas-49/uber_-streaming_project_azure) for the event-processing portion.
