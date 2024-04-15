## Folder Structure

```
solution name/
  meta/
    meta.yml
    icon.png
    schema.json
    style.json
    Insights*.json
    queriesDocs.json
    images/
  schema/
    schema.gsql
  queries/
  data/
  loading_job/
  udfs/
  reset/
```

1. The top-level folder names, such as `meta` or `schema`, within the solution folder are based on convention and cannot be changed. Only folders containing `meta/meta.yml` are recognized as solutions.

2. The `meta` folder contains metadata about the solution.

   - `meta/schema.json` contains the API response from `/api/gsql-server/gsql/schema` for the schema. We need this in advance so we can show the schema in the UI before creating the schema.
   - `meta/style.json` contains the API response from `/api/graph-styles/local/${graphName}` for the style. We need this in advance so we can show the style (the vertex's color and position) in the UI before creating the schema. This file is optional.
   - `meta/Insights*.json` contains the exported insights application configuration. If it exists, we will import the insights application when installing the solution.
   - `meta/metadata_descriptor.json` currently contains description for query. We will send it to copilot when install solution.
   - `meta/icon.png`|`meta/icon.jpg` is the icon of the solution.
   - `meta/images` contains the images to better describe the solution.

3. The `data` folder will contain the sample data. For example, if the data is at `financial_crime/transaction_fraud/transaction_fraud/data`, we will upload this folder to `s3://tigergraph-solution-kits/financial_crime/transaction_fraud/transaction_fraud/data` when merging into the master branch.

4. The `loading_job` folder contains the loading job for loading sample data.

5. `udfs` contains the UDFs for the solution.

6. The `reset` folder is used to clean the database.

## Meta File Format

```yaml
metadata:
  name: Anti-Fraud
  graph: AntiFraud
  description: This is a description
  provider: TigerGraph
  is_library: true
  categories:
    - Fraud
    - Financial
  algorithms:
    - Page Rank

queries:
  first:
    - use_graph.gsql
  last:
    - install_query.gsql
```

1. The `metadata` section contains basic information about the solution, such as its name, description, categories and graph name, the `provider` is default to tigergraph.

2. `is_library` indicate if this solution is a library, default to false.

3. The algorithms list all the graph algorithms used in the solution.

4. The `first` and `last` sections are used to control the order of the queries. The queries listed under `first` will be executed first, and the queries listed under `last` will be executed last.

5. Queries are not installed automatically. If you want to install your query, you should create a separate file in the `queries` folder and add it to the `last` file list as follows:
   ```sql
   USE GRAPH <your_graph_name>
   INSTALL QUERY ALL
   ```

## S3 bucket layout

```
tigergraph-solution-kits
  list.json
  financial_crime/transaction_fraud/transaction_fraud/
    meta.json
    data/
    meta/
      images/
      icon.png
      application.json
```
