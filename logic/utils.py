import requests
import xml.etree.ElementTree as ET

def get_files_properties(folder_urls, from_metalink=True):
    file_urls = []
    file_sizes = []
    file_updates = []
    
    for folder_url in folder_urls:
        if from_metalink:
            metalink_response = requests.get(folder_url, headers={"Accept": "application/metalink4+xml"})
            if metalink_response.status_code == 200:
                tree = ET.ElementTree(ET.fromstring(metalink_response.content))
                root = tree.getroot()
                
                file_elements = root.findall('.//{urn:ietf:params:xml:ns:metalink}file')
                for element in file_elements:
                    url = element.find('{urn:ietf:params:xml:ns:metalink}url')
                    size = element.find('{urn:ietf:params:xml:ns:metalink}size')
                    updated = element.find('{urn:ietf:params:xml:ns:metalink}updated')

                    file_urls.append(url.text if url is not None else None)
                    file_sizes.append(size.text if size is not None else None)
                    file_updates.append(updated.text if updated is not None else None)
            else:
                raise RuntimeError(f"Failed to fetch Metalink XML from {folder_url} (status code: {metalink_response.status_code})")
    
    return file_urls, file_sizes, file_updates

def get_digests(urls):
    headers = {
        "Want-Digest": "ADLER32"
    }
    digests = []
    for url in urls:
        response = requests.head(url, headers=headers)
        if response.status_code == 200:
            digest = response.headers.get('Digest')
            if digest:
                digests.append(digest)
            else:
                print("No Digest header found.")
        else:
            print(f"Failed to fetch headers. Status code: {response.status_code}")
    return digests