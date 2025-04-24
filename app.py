from flask import Flask, jsonify, request, Response
import requests
import os
import json

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

def construct_jsonld(metadata, download_urls):
    distributions = [
        {
            "@type": "DataDownload",
            "contentUrl": url,
            # "encodingFormat": "application/zip"
        } for url in download_urls
    ]

    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": metadata.get("doi"),
        "name": metadata.get("title"),
        "description": metadata.get("dataDescription"),
        "distribution": distributions  # List of all download URLs
    }

@app.route("/doi/<path:doi>")
def serve_doi_metadata(doi):
    try:
        accept = request.headers.get("Accept", "")

        encoded_doi = doi.replace("/", "%2F")
        metadata, ids = fetch_PublishedData_ids(encoded_doi)
        encoded_ids = [id.replace("/", "%2F") for id in ids]
        folders = fetch_datasets_folders(encoded_ids)
        download_urls = [STORAGE_BASE_URL + folder for folder in folders]
        jsonld = construct_jsonld(metadata, download_urls)

        if "application/ld+json" in accept:
            return Response(
                response=jsonify(jsonld).data,
                status=200,
                mimetype='application/ld+json'
            )
        elif "text/html" in accept or "*/*" in accept:
            html_resp = requests.get("http://localhost/index.html")  # request from NGINX
            html = html_resp.text
            injected = html.replace(
                "<head>",
                f"<head>\n<script type='application/ld+json'>\n{json.dumps(jsonld)}\n</script>\n"
            )
            return Response(injected, mimetype="text/html")

        else:
            return jsonify({"error": "Unsupported Accept header"}), 406
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/script/<path:doi>")
def inject_script(doi):
    html_resp = requests.get("http://localhost/index.html")  # request from NGINX
    html = html_resp.text

    # Directly fetch the raw JSON-LD data
    encoded_doi = doi.replace("/", "%2F")
    metadata, ids = fetch_PublishedData_ids(encoded_doi)
    encoded_ids = [id.replace("/", "%2F") for id in ids]
    folders = fetch_datasets_folders(encoded_ids)
    download_urls = [STORAGE_BASE_URL + folder for folder in folders]
    jsonld = construct_jsonld(metadata, download_urls)

    injected = html.replace(
        "<head>",
        f"<head>\n<script type='application/ld+json'>\n{json.dumps(jsonld)}\n</script>\n"
    )

    return Response(injected, mimetype="text/html")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
