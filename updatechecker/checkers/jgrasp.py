import hashlib
import re

from bs4 import BeautifulSoup
import checker

_JGRASP_DOMAIN = 'https://jgrasp.org'
_JGRASP_DOWNLOAD_PAGE = 'https://spider.eng.auburn.edu/user-cgi/grasp/grasp.pl'
_JGRASP_DOWNLOAD_ARGS = { ';dl': 'download_jgrasp.html' }
_DOWNLOAD_SUBDIR = 'dl4g'
_PARSER = 'html.parser'

# The jGRASP downloads seem to shed all the separators between the different
# fields of the version number except for the underscore. This regex attempts
# to parse that back to a recognizable version numer.
_VERSION_REGEX = re.compile(
    r"jgrasp"           # The download name will always start with jgrasp
    r"(?P<major>\d)"    # The major seems to always be a single digit
    r"(?P<minor>\d)"    # This seems to also always be a single digit
    r"(?P<patch>\d+)"   # This accepts multiple digits to prevent parsing fails
    r"(?P<extra>_\d+)?" # Any number of digits are accepted, but usually its 2
    r"(?P<beta>b"
    r"(?P<beta_num>\d+)?"
    r")?"
)

class JGraspChecker(checker.BaseUpdateChecker):

    name = 'jGRASP'

    def _path_to_version(self, path):
        match = _VERSION_REGEX.search(path)
        major = match.group('major')
        minor = match.group('minor')
        patch = match.group('patch')
        extra = match.group('extra')
        
        version_str = f'{major}.{minor}.{patch}{extra}'

        if self.beta:
            beta_num = match.group('beta_num') or ""
            version_str = f'{version_str} Beta {beta_num}'
            if not beta_num:
                version_str = version_str[:-1]

        return version_str

    def _load(self):
        download_page = self.session.get(_JGRASP_DOWNLOAD_PAGE, params=_JGRASP_DOWNLOAD_ARGS)
        soup = BeautifulSoup(download_page.content, _PARSER)
        if self.beta:
            target = ';target23'
        else:
            target = ';target3'
        try:
            path = soup.find_all(attrs={'name': target})[0].get('value')
        except IndexError:
            return None
        self._latest_url = f'{_JGRASP_DOMAIN}/{_DOWNLOAD_SUBDIR}/{path}'
        self._latest_version = self._path_to_version(path)
        data = self.session.get(self.latest_url).content
        self._sha1_hash = hashlib.sha1(data).hexdigest()
