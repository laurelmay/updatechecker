import hashlib
from urllib.parse import urlparse, parse_qs

from updatechecker import checker

DOWNLOAD_ROOT = "https://download.virtualbox.org/virtualbox"


class VirtualBoxGuestAdditionChecker(checker.BaseUpdateChecker):
    """
    Check for updates for the VirtualBox Guest Additions
    """

    name = "VirtualBox Guest Additions"
    short_name = "vbox-guest"

    def latest_data_url(self):
        if self.beta:
            return f"{DOWNLOAD_ROOT}/LATEST-BETA.TXT"
        return f"{DOWNLOAD_ROOT}/LATEST.TXT"

    async def _load(self):
        async with self.session.get(self.latest_data_url()) as version_data_response:
            release = (await version_data_response.read()).decode('utf-8').strip()

        self._latest_version = release
        self._latest_url = f"{DOWNLOAD_ROOT}/{release}/VBoxGuestAdditions_{release}.iso"

        # VirtualBox provides SHA256 and MD5 hashes but not SHA1
        async with self.session.get(self._latest_url) as file_response:
            data = await file_response.read()
        
        self._sha1_hash = hashlib.sha1(data).hexdigest()
