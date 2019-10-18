import hashlib

from bs4 import BeautifulSoup
from updatechecker.checker import BaseUpdateChecker

_JGRASP_DOMAIN = 'https://jgrasp.org'
_JGRASP_DOWNLOAD_PAGE = 'https://spider.eng.auburn.edu/user-cgi/grasp/grasp.pl'
_JGRASP_DOWNLOAD_ARGS = { ';dl': 'download_jgrasp.html' }
_DOWNLOAD_SUBDIR = 'dl4g'
_PARSER = 'html.parser'


class JGraspChecker(BaseUpdateChecker):
    def get_latest(self):
        download_page = self.session.get(_JGRASP_DOWNLOAD_PAGE, params=_JGRASP_DOWNLOAD_ARGS)
        soup = BeautifulSoup(download_page.content, _PARSER)
        path = soup.find_all(attrs={'name': ';target3'})[0].get('value')
        self.latest_url = f'{_JGRASP_DOMAIN}/{_DOWNLOAD_SUBDIR}/{path}'
        return self.latest_url

    def get_sha1_hash(self):
        if not self.latest_url:
            self.get_latest()
        
        file = self.session.get(self.latest_url).content
        self.latest_sha1 = hashlib.sha1(file).hexdigest()
        return self.latest_sha1