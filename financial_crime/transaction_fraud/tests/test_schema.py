import pytest

class TestSchema:
    """
    A class for testing graph schema
    """
    def test_conn(self, tg_conn):
        """
        Pings the TigerGraph Database to check if the connection has been correctly set up
        """
        
        response = tg_conn.echo()
        assert response == "Hello GSQL", "Did not successfully connect to TigerGraph"

    def test_get_vertices(self, tg_conn, all_vertices):
        """
        Checks all vertices loaded into the schema correctly
        """

        response = tg_conn.getVertexTypes()
        assert response == list(all_vertices.keys()), "Vertices did not load correctly"

    def test_get_edges(self, tg_conn, all_edges):
        """
        Check all edges loaded into schema correctly
        """

        response = tg_conn.getEdgeTypes(force=True)
        assert response == list(all_edges.keys()), "Edges did not load correctly"

    def test_edge_vertices(self, tg_conn, all_edges, edge_info):
        """
        Checks all edges have the correct source and target vertex
        """
        edge_dict = {}
        for e in all_edges:
            source = tg_conn.getEdgeSourceVertexType(e)
            target = tg_conn.getEdgeTargetVertexType(e)

            edge_dict[e] = [source, target]
        
        assert edge_dict == edge_info, "Edge source and target do not match"