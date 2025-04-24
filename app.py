from flask import Flask, jsonify, request, Response
import requests
import os
import json
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

SCICAT_BASE_URL = os.environ.get("SCICAT_BASE_URL", "https://public-data-dev.desy.de/api/v3")
STORAGE_BASE_URL = os.environ.get("STORAGE_BASE_URL", "https://hifis-storage.desy.de:2880")

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

def construct_jsonld(metadata, folder_urls):
    distributions = [
        {
            "@type": "DataDownload",
            "contentUrl": url,
            # "encodingFormat": "application/zip"
        } for url in folder_urls
    ]

    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": metadata.get("doi"),
        "name": metadata.get("title"),
        "description": metadata.get("dataDescription"),
        "distribution": distributions 
    }

def construct_metalink(metadata, file_urls):
    metalink = ET.Element("metalink", xmlns="urn:ietf:params:xml:ns:metalink")

    ET.SubElement(metalink, "identity", name=metadata.get("title"))
    ET.SubElement(metalink, "name", name=metadata.get("title"))
    ET.SubElement(metalink, "description", name=metadata.get("dataDescription"))

    for url in file_urls:
        file_name = url.split("/")[-1]
        file_el = ET.SubElement(metalink, "file", name=file_name)
        ET.SubElement(file_el, "url").text = url

    return ET.tostring(metalink, encoding="utf-8", xml_declaration=True).decode("utf-8")

def get_file_urls(folder_urls, from_metalink=True):
    file_urls = []
    for url in folder_urls:
        if from_metalink:
            metalink_response = requests.get(url, headers={"Accept": "application/metalink4+xml"})
            if metalink_response.status_code == 200:
                tree = ET.ElementTree(ET.fromstring(metalink_response.content))
                root = tree.getroot()
                
                folder_elements = root.findall('.//{urn:ietf:params:xml:ns:metalink}file')
                for element in folder_elements:
                    file_url = element.find('{urn:ietf:params:xml:ns:metalink}url').text
                    file_urls.append(file_url)
            else:
                return jsonify({"error": f"Failed to fetch Metalink XML from {url}"}), 500
    return file_urls


@app.route("/doi/<path:doi>")
def serve_doi_metadata(doi):
    try:
        accept = request.headers.get("Accept", "")

        encoded_doi = doi.replace("/", "%2F")
        metadata, ids = fetch_PublishedData_ids(encoded_doi)
        encoded_ids = [id.replace("/", "%2F") for id in ids]
        folders = fetch_datasets_folders(encoded_ids)
        folder_urls = [STORAGE_BASE_URL + folder for folder in folders]

        # get_file_urls_from_metalinks(folder_urls)

        if "application/ld+json" in accept:
            jsonld = construct_jsonld(metadata, folder_urls)
            return Response(
                response=jsonify(jsonld).data,
                status=200,
                mimetype='application/ld+json'
            )
        if "application/metalink4+xml" in accept:
            # metalink_url = folder_urls[0]
            # metalink_response = requests.get(metalink_url, headers={"Accept": "application/metalink4+xml"})

            # if metalink_response.status_code == 200:
            #     return Response(
            #         metalink_response.content,
            #         status=200,
            #         mimetype="application/metalink4+xml"
            #     )
            # else:
            #     return jsonify({"error": "Failed to fetch Metalink XML from the URL."}), 500

            file_urls = get_file_urls(folder_urls, from_metalink=True)
            logging.debug(f'files urls: {file_urls}')
            metalink_xml = construct_metalink(metadata, file_urls)
            return Response(
                metalink_xml,
                status=200,
                mimetype="application/metalink4+xml"
            )

        elif "text/html" in accept or "*/*" in accept:
            html_resp = requests.get("http://localhost/index.html")  # request from NGINX
            html = html_resp.text
            injected = html.replace(
                "<head>",
                f"<head>\n<script type='application/ld+json'>\n{json.dumps(jsonld, indent=2)}\n</script>\n"
            )
            return Response(injected, mimetype="text/html")

        else:
            return jsonify({"error": "Unsupported Accept header"}), 406
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
