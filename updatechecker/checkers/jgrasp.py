from updatechecker.checker import BaseUpdateChecker
from bs4 import BeautifulSoup

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
        return f'{_JGRASP_DOMAIN}/{_DOWNLOAD_SUBDIR}/{path}'
