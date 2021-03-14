import xml.etree.ElementTree as ET

import requests
import checker

API_ENDPOINT = "https://api.eclipse.org/download/release/eclipse_packages"


def _latest_version_name(release_file, beta):
    root = ET.fromstring(release_file)
    if beta:
        latest = root.find("future").text
    else:
        latest = root.find("present").text
    return latest


def _java_release_name(java_file):
    try:
        root = ET.fromstring(java_file)
    except:
        print("Invalid XML")
        print(java_file)
        raise

    name = root.find("product").get("name")
    return name


class EclipseJavaChecker(checker.BaseUpdateChecker):

    name = "Eclipse IDE for Java Developers"
    short_name = "eclipse-java"

    def _load(self):
        version_data = self.session.get(API_ENDPOINT).json()
        release = version_data["release_name"]
        download_url = version_data["packages"]["java-package"]["files"]["linux"]["64"][
            "url"
        ]
        self._latest_version = release
        self._latest_url = download_url

        sha_hash = requests.get(f"{download_url}.sha1").content
        self._sha1_hash = sha_hash.decode("ascii")
