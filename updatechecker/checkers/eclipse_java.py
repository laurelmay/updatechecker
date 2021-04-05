from urllib.parse import urlparse, parse_qs

import requests

from updatechecker import checker

DOWNLOAD_DOMAIN = "download.eclipse.org"
API_ENDPOINT = "https://api.eclipse.org/download/release/eclipse_packages"


def _build_download_url(redirect):
    parsed_url = urlparse(redirect)
    query_data = parse_qs(parsed_url.query)
    file_path = query_data["file"][0]
    return f"https://{DOWNLOAD_DOMAIN}{file_path}"


def _dict_query(d, query):
    if not query:
        return d
    queries = query.split(".")
    return _dict_query(d[queries[0]], ".".join(queries[1:]))


class EclipseJavaChecker(checker.BaseUpdateChecker):
    """
    Check for updates for the Eclipse IDE for Java Developers
    """

    name = "Eclipse IDE for Java Developers"
    short_name = "eclipse-java"

    def _load(self):
        version_data = self.session.get(API_ENDPOINT).json()
        release = version_data["release_name"]
        redirect_url = _dict_query(
            version_data, "packages.java-package.files.linux.64.url"
        )
        download_url = _build_download_url(redirect_url)
        self._latest_version = release
        self._latest_url = download_url

        sha_hash = requests.get(f"{download_url}.sha1").content
        self._sha1_hash = sha_hash.decode("ascii").split()[0]
