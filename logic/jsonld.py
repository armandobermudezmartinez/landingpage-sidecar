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