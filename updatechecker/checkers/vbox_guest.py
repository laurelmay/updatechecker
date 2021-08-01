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

    def _load(self):
        if self.beta:
            version_data_response = self.session.get(f"{DOWNLOAD_ROOT}/LATEST-BETA.TXT")
        else:
            version_data_response = self.session.get(f"{DOWNLOAD_ROOT}/LATEST.TXT")
        version_data_response.raise_for_status()
        release = version_data_response.content.decode('utf-8').strip()
        self._latest_version = release
        self._latest_url = f"{DOWNLOAD_ROOT}/{release}/VBoxGuestAdditions_{release}.iso"

        # VirtualBox provides SHA256 and MD5 hashes but not SHA1
        file_response = self.session.get(self._latest_url)
        file_response.raise_for_status()
        data = file_response.content
        self._sha1_hash = hashlib.sha1(data).hexdigest()
