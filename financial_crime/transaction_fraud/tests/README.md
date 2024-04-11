# Solution Kit Test

This is an example of what unit testing a solution kit could look like. The test in these modules are broken into Schema, Data Loading, and Querying.

The test uses an empty instace on TGCloud, it creates the graph, schema, loads the data, and performs an intial query. Expected results are defined through fixtures in the `conftest.py` file as well as any intial set up and tear downs.

Recommended way to run the test with all the outputs is:
```
python3 -m pytest -s -vv --drop=False
```

The drop flag tells the test whether to tear down everything after or leave it in place. Setting it to true results in `DROP ALL`.

### Required Libraries
- pandas
- python-dotenv
- pyTigerGraph
- pathlib
- shutil

### Notes
There will be some errors arould SSL, to disable it run the following commands

``` 
export PYTHONWARNINGS="ignore:Unverified HTTPS request" 
```

```
pip3 install urllib3==1.26.6
```
