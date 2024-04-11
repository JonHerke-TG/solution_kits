import pytest
import os
import time

class TestQueries:
    """
    A class for testing queries
    """

    def test_query_upload(self, graphname, tg_conn, query_data):
        """
        Upload all queries from the queries folder
        """

        use_graph_str = "USE GRAPH {}".format(graphname)
        for filename in os.listdir(query_data["query_dir"]):
            query_file = data_file = os.path.join(query_data["query_dir"], filename)
            with open(query_file, 'r') as file:
                gsql_cmd = file.read()
            tg_conn.gsql(use_graph_str + " " + gsql_cmd)
        
        # Install Queries
        tg_conn.gsql(use_graph_str + " INSTALL QUERY ALL")

        # Check if returned install queries match expected value
        res = tg_conn.getInstalledQueries()
        assert list(res.keys()).sort() == query_data["endpoints"].sort()

    
    def test_card_transaction_stats(self, tg_conn, card_stats_expected_results):
        """
        Tests the card transaction stats query, this can be parmeterized for more values
        """
        res = tg_conn.runInstalledQuery(queryName = 'card_transactions_stats', params={"v":card_stats_expected_results["id"]})
        assert res == card_stats_expected_results["stats"]
        
        







