import pytest
import shutil
import os
import json
import time

class TestData:
    """
    A class for testing graph data laoding jobs
    """
    def test_conn(self, tg_conn):
        """
        Pings the TigerGraph Database to check if the connection has been correctly set up
        """
        
        response = tg_conn.echo()
        assert response == "Hello GSQL", "Did not successfully connect to TigerGraph"

    def test_create_load_data_job(self, tg_conn, load_data):
        """
        Creates loading job, requires a loading job that does not define the file path or run the loading job as that is done by test_data_load
        """
        # Create Graph with Schema File
        with open(load_data["file_name"], 'r') as file:
            gsql_cmd = file.read()
        response = tg_conn.gsql(gsql_cmd)
        assert response == "Using graph 'Transaction_Fraud'\nSuccessfully created loading jobs: [{}].".format(load_data["job_name"])

    def test_load_data(self, tg_conn, load_data, all_vertices, all_edges):
        """
        Loads all data files 
            - Ran into some issues where there was a delay in when the data was uploaded and when it showed in subsequent tests so 
                introduced a sleep timer in here for now
        """

        for filename in os.listdir(load_data["file_path"]):
            data_file = os.path.join(load_data["file_path"], filename)
            results = tg_conn.runLoadingJobWithFile(filePath=data_file, fileTag='MyDataSource', jobName='loading_data', sep='|', timeout=600000)
            print("Loaded data from{}".format(data_file))
            time.sleep(5)
    
        time.sleep(60)
        assert True

    def test_vertex_count(self, tg_conn, all_vertices):
        """
        Tests that vertex counts are as expected
        """
        res = tg_conn.getVertexCount() 
        assert res == all_vertices
    

    def test_edge_count(self, tg_conn, all_edges, reverse_edges):
        """
        Tests edge counts are as expected
            - Reverse edges show up in this call but not in the schema call so introduced it as a seperate dictionary to check
        """
        res = tg_conn.getEdgeCount()
        assert res == {**all_edges, **reverse_edges}




        
        

