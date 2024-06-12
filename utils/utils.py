import requests
from requests.auth import HTTPBasicAuth


def insert_data_to_graphdb(graph, graphdb_url, username, password):
    data = graph.serialize(format='nt')

    headers = {
        'Content-Type': 'application/x-turtle'
    }

    response = requests.post(graphdb_url, data=data, headers=headers, auth=HTTPBasicAuth(username, password))

    if response.status_code == 204:
        print("Data inserted successfully.")
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)
