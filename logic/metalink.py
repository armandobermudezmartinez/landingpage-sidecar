import xml.etree.ElementTree as ET
import urllib.parse

def construct_metalink(metadata, urls, sizes, updates, digests):
    metalink = ET.Element("metalink", xmlns="urn:ietf:params:xml:ns:metalink")

    ET.SubElement(metalink, "identity", name=metadata.get("title"))
    ET.SubElement(metalink, "name", name=metadata.get("title"))
    ET.SubElement(metalink, "description", name=metadata.get("dataDescription"))

    for url, size, updated, digest in zip(urls, sizes, updates, digests):
        encoded_file_name = url.split("/")[-1]
        file_name = urllib.parse.unquote(encoded_file_name)

        file_element = ET.SubElement(metalink, "file", name=file_name)
        hash_type, hash_value = digest.split('=', 1)
        ET.SubElement(file_element, "size").text = size
        ET.SubElement(file_element, "url").text = url
        ET.SubElement(file_element, "updated").text = updated
        hash_element = ET.SubElement(file_element, "hash", type=hash_type)
        hash_element.text = hash_value

    return ET.tostring(metalink, encoding="utf-8", xml_declaration=True).decode("utf-8")

