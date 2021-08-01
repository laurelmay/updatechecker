import hashlib
import re
import urllib.parse

from bs4 import BeautifulSoup

from updatechecker import checker

_FINCH_DOMAIN = "https://www.birdbraintechnologies.com"
_DOWNLOAD_PAGE = "https://www.birdbraintechnologies.com/finch1/python/install/"
_PARSER = "html.parser"
_LINUX_TEXT = "Linux (Ubuntu)"

_VERSION_REGEX = re.compile(r"FinchPython(?P<major>\d)(?P<minor>\d+)?\.zip")


class FinchChecker(checker.BaseUpdateChecker):
    """
    Check for updates to the Finch 1 Robot Python library.
    """

    name = "Finch Python"
    short_name = "finch"

    def _path_to_version(self, path):
        parsed = urllib.parse.urlparse(path)
        match = _VERSION_REGEX.search(path)
        major = match.group("major")
        minor = match.group("minor")

        return f"{major}.{minor}"

    def _load(self):
        download_page = self.session.get(_DOWNLOAD_PAGE)
        download_page.raise_for_status()
        soup = BeautifulSoup(download_page.content, _PARSER)
        download_link = soup.find_all("a", string=_LINUX_TEXT, limit=1)[0].get("href")

        self._latest_url = f"{_FINCH_DOMAIN}{download_link}"
        self._latest_version = self._path_to_version(self._latest_url)
        file_response = self.session.get(self._latest_url)
        file_response.raise_for_status()
        data = file_response.content
        self._sha1_hash = hashlib.sha1(data).hexdigest()
