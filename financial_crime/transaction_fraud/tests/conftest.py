import pytest
import pyTigerGraph as tg
import json
import pathlib
import os
import shutil
from dotenv import load_dotenv

# Load Env Variables
load_dotenv()


def drop_graph(conn = None, graphname = None):
    """ Drops everything from the instance

    Args:
        connection:
            TigerGraph Connection 
    """
    # Drop everything
    print("\n Dropping Graph {}".format(graphname))
    conn.gsql(""" USE GLOBAL
        DROP ALL """)
    print("\n Graph {} Dropped".format(graphname))

# Loads graphname from env and returns it
@pytest.fixture(scope="session")
def graphname():
    graphname = os.getenv("graphname")
    return graphname


@pytest.fixture(scope="session")
def tg_conn(pytestconfig, graphname):
    """
    A fixture to create the TigerGraph "connection"

    Returns:
        REST APIs to communicate with TigerGraph Database

    """

    # Load Env Variables and Schema File Path
    hostName = os.getenv("hostName")
    userName = os.getenv("userName")
    password = os.getenv("password")

    schema_file = "../1_create_schema.gsql"

    # Establish Connection
    conn = tg.TigerGraphConnection(host=hostName, username=userName, password=password)

    # Create Graph with Schema File
    with open(schema_file, 'r') as file:
        gsql_cmd = file.read()
    
    # In case Graph already exists this will fail silently 
    try:
        conn.gsql(gsql_cmd)
    except:
        pass
        
    # Add Graph Name
    conn.graphname = graphname

    # Create token and attach token 
    conn.apiToken = conn.getToken(conn.createSecret())

    yield conn

    if pytestconfig.getoption("drop"):
        drop_graph(conn)



# SCHEMA FIXTURES
##############################

@pytest.fixture(scope="function")
def all_vertices():
    vertices = {'Community': 0 , 'Address': 1000, 'City': 736, 'Merchant': 694, 'State': 51, 'Zipcode': 963, 'Payment_Transaction': 210590, 
                'Card': 999, 'Merchant_Category': 15, 'Party': 1694, 
                'Phone': 1000, 'Email': 998, 'IP': 1000, 'Device': 1000, 'ID': 1000, 'Full_Name': 998, 'DOB': 989}
    return vertices

@pytest.fixture(scope="function")
def all_edges():
    edges = {'Merchant_Merchant': 0, 'Merchant_Receive_Transaction': 846202, 'Card_Send_Transaction': 860141, 'Card_Card':0, 
            'Merchant_Assigned':701, 'Is_SubCategory':0, 'Has_Interaction_With_Merchant':406019, 'Has_Address':1000, 'Is_Merchant':694, 
            'Party_Has_Card':999, 'Has_Phone':1000, 'Has_Email':1000, 'Has_Community':0, 
            'Has_ID':1000, 'Has_IP':1000, 'Has_Device':1000, 'Assigned_To':1968, 'Located_In':1796, 
            'Has_DOB':1003, 'Has_Full_Name':1002}
    return edges

@pytest.fixture(scope="function")
def edge_info():
    edge_info = {'Merchant_Merchant': ['Merchant', 'Merchant'], 'Merchant_Receive_Transaction': ['Payment_Transaction', 'Merchant'], 
                'Card_Send_Transaction': ['Payment_Transaction', 'Card'], 'Card_Card': ['Card', 'Card'], 'Merchant_Assigned': ['Merchant', 'Merchant_Category'], 
                'Is_SubCategory': ['Merchant_Category', 'Merchant_Category'], 'Has_Interaction_With_Merchant': ['Card', 'Merchant'], 
                'Has_Address': ['Address', 'Party'], 'Is_Merchant': ['Merchant', 'Party'], 'Party_Has_Card': ['Party', 'Card'], 'Has_Phone': ['Party', 'Phone'], 
                'Has_Email': ['Party', 'Email'], 'Has_Community': [{'Party', 'Merchant', 'Card'}, 'Community'], 'Has_ID': ['Party', 'ID'], 
                'Has_IP': ['Party', 'IP'], 'Has_Device': ['Party', 'Device'], 'Assigned_To': [{'Address', 'Zipcode'}, {'City', 'Zipcode'}], 
                'Located_In': [{'Address', 'City'}, {'State', 'City'}], 'Has_DOB': ['Party', 'DOB'], 'Has_Full_Name': ['Party', 'Full_Name']}
    return edge_info

@pytest.fixture(scope="function")
def reverse_edges():
    return {'reverse_Is_SubCategory': 0}


# LOAD DATA FIXTURES
####################
@pytest.fixture(scope="module")
def load_data():
    load_data_file = "2_load_data_test.gsql"
    loading_job_name = "loading_data"
    file_path = "/Users/hunaidshakoor/Documents/solution_kits/financial_crime/transaction_fraud/data"
    return {"file_name": load_data_file, "job_name":loading_job_name, "file_path":file_path}

# QUERY FIXTURES
#####################
@pytest.fixture(scope="function")
def query_data(graphname):
    query_dir = '/Users/hunaidshakoor/Documents/solution_kits/financial_crime/transaction_fraud/queries'
    endpoint_fmt = "GET /query/{}/".format(graphname)
    query_endpoints = []
    # create query endpoints
    for filename in os.listdir(query_dir):
        query_endpoint = endpoint_fmt+os.path.splitext(filename)[0]
        query_endpoints.append(query_endpoint)

    return {'query_dir': query_dir, 'endpoints': query_endpoints}

@pytest.fixture(scope="function")
def card_stats_expected_results():
    card_id = 676134761284
    stats =[
            {
                "rlt": [
                {
                    "attributes": {
                    "Average_Transaction_Amount": 86.73304761904747,
                    "Maximum_Transaction_Amount": 1215.85,
                    "Minimum_Transaction_Amount": 1,
                    "Total_Transaction_Amount": 63748.77,
                    "Transaction_Count": 735
                    },
                    "v_id": "676134761284",
                    "v_type": "Card"
                }
                ]
            }
            ]
    return {"id": card_id, "stats": stats}


###################
# SET UP TESTING ORDER
###################    
def pytest_collection_modifyitems(items):
    """Modifies test items in place to ensure test classes run in a given order."""
    CLASS_ORDER = ["TestSchema", "TestData", "TestQueries"]
    class_mapping = {item: item.cls.__name__ for item in items}

    sorted_items = items.copy()
    # Iteratively move tests of each class to the end of the test queue
    for class_ in CLASS_ORDER:
        sorted_items = [it for it in sorted_items if class_mapping[it] != class_] + [
            it for it in sorted_items if class_mapping[it] == class_
        ]
    items[:] = sorted_items

def pytest_addoption(parser):
    parser.addoption("--drop", action="store", default=True)

