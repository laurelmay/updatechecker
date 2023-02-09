import json

from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

from updatechecker import checker

DOWNLOAD_DOMAIN = "download.eclipse.org"
API_ENDPOINT = "https://api.eclipse.org/download/release/eclipse_packages"
RELEASE_BASE_URL = "https://download.eclipse.org/technology/epp/downloads/release"
RELEASE_FILE = f"{RELEASE_BASE_URL}/release.xml"


class EclipseApiDataError(Exception):
    def __init__(self, query, api_data):
        json_str = json.dumps(api_data)
        super().__init__(f"{query}: {json_str}")
        self.query = query
        self.api_data = api_data

class EclipseDataParsingError(Exception):
    def __init__(self, url, message):
        super().__init__(f"Unable to parse {url}: {message}")
        self.url = url

def _build_download_url(redirect):
    parsed_url = urlparse(redirect)
    query_data = parse_qs(parsed_url.query)
    file_path = query_data["file"][0]
    return f"https://{DOWNLOAD_DOMAIN}{file_path}"


def _dict_query(d, query):
    if not query:
        return d
    queries = query.split(".")
    if queries[0] not in d:
        return None
    return _dict_query(d[queries[0]], ".".join(queries[1:]))


class EclipseJavaChecker(checker.BaseUpdateChecker):
    """
    Check for updates for the Eclipse IDE for Java Developers
    """

    name = "Eclipse IDE for Java Developers"
    short_name = "eclipse-java"
    ignored = True
    arch = None

    async def _load(self):
        async with self.session.get(RELEASE_FILE) as version_data_response:
            response_body = await version_data_response.text('utf-8')
        version_data = ET.fromstring(response_body)
        version_type = 'future' if self.beta else 'present'
        present = version_data.find(version_type)
        if present is None:
            raise EclipseDataParsingError(RELEASE_FILE, f"No '{version_type}' key")
        release_text = present.text
        if not release_text:
            raise EclipseDataParsingError(RELEASE_FILE, f"No text for '{version_type}'")
        [release_name, release_type] = release_text.split('/')
        download_url = f"{RELEASE_BASE_URL}/{release_text}/eclipse-java-{release_name}-{release_type}-linux-gtk-{self.arch}.tar.gz"
        sha_url = f"{download_url}.sha1"
        async with self.session.get(sha_url) as sha_hash_request:
            sha_hash = await sha_hash_request.text('utf-8')

        self._latest_version = release_name
        self._latest_url = download_url
        self._sha1_hash = sha_hash.split()[0]


class EclipseJavaCheckerx8664(EclipseJavaChecker):
    name = "Eclipse IDE for Java Developers (x86_64)"
    short_name = "eclipse-java-x86_64"
    ignored = False
    arch = "x86_64"


class EclipseJavaCheckerAarch64(EclipseJavaChecker):
    name = "Eclipse IDE for Java Developers (ARM64)"
    short_name = "eclipse-java-arm64"
    ignored = False
    arch = "aarch64"
