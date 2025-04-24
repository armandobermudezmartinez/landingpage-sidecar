from flask import Flask, jsonify, request, Response
import requests
import json
from logic.utils import get_files_properties, get_digests
from logic.scicat_utils import fetch_PublishedData_ids, fetch_folders_urls
from logic.jsonld import construct_jsonld
from logic.metalink import construct_metalink

app = Flask(__name__)

@app.route("/doi/<path:doi>")
def serve_doi_metadata(doi):
    try:
        accept = request.headers.get("Accept", "")

        encoded_doi = doi.replace("/", "%2F")
        metadata, ids = fetch_PublishedData_ids(encoded_doi)
        encoded_ids = [id.replace("/", "%2F") for id in ids]
        folder_urls = fetch_folders_urls(encoded_ids)
        jsonld = construct_jsonld(metadata, folder_urls)

        if "application/ld+json" in accept:
            return Response(
                response=jsonify(jsonld).data,
                status=200,
                mimetype='application/ld+json'
            )
        
        if "application/metalink4+xml" in accept:
            urls, sizes, updates = get_files_properties(folder_urls, from_metalink=True)
            digests = get_digests(urls)

            metalink_xml = construct_metalink(metadata, urls, sizes, updates, digests)
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
