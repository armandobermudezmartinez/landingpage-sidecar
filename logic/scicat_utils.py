import requests
import os

SCICAT_BASE_URL = os.environ.get("SCICAT_BASE_URL", "https://public-data-dev.desy.de/api/v3")

def fetch_PublishedData_ids(doi):
    url = f"{SCICAT_BASE_URL}/PublishedData/{doi}"
    response = requests.get(url)
    response.raise_for_status()
    metadata = response.json()
    pids = metadata["pidArray"]
    return metadata, pids

def fetch_datasets_folders(pids):
    folders = []
    for pid in pids:
        url = f"{SCICAT_BASE_URL}/datasets/{pid}"
        response = requests.get(url)
        response.raise_for_status()
        folders.append(response.json()["sourceFolder"])
    return folders