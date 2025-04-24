import requests
from config import SCICAT_BASE_URL, STORAGE_BASE_URL

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

def fetch_folders_urls(pids):
    folders = fetch_datasets_folders(pids)
    return [STORAGE_BASE_URL + folder for folder in folders]