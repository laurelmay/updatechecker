import xml.etree.ElementTree as ET
from updatechecker import checker

_LINUX_SUFFIX = '-linux-gtk-x86_64.tar.gz'


def _latest_version_directory(release_file, beta):
    root = ET.fromstring(release_file)
    if beta:
        latest = root.find('future').text
    else:
        latest = root.find('present').text
    return latest


def _java_release_name(java_file):
    try:
        root = ET.fromstring(java_file)
    except:
        print("Invalid XML")
        print(java_file)
        raise

    name = root.find('product').get('name')
    return name


class EclipseJavaChecker(checker.BaseUpdateChecker):

    def get_latest(self, beta=False):
        mirror_url = self.context['eclipse']['mirror_url']
        release_file = f'{mirror_url}/release.xml'
        response = self.session.get(release_file)
        if not response:
            raise ValueError(f"Error accessing {release_file}: {response}")
        release_dir = _latest_version_directory(response.content, beta)
        java_release_file = f'{mirror_url}/{release_dir}/java.xml'
        response = self.session.get(java_release_file)
        if not response:
            raise ValueError(f"Error accessing {java_release_file}: {response}")
        java_name = _java_release_name(response.content)
        self.latest_url =  f'{mirror_url}/{release_dir}/{java_name}{_LINUX_SUFFIX}'
        return self.latest_url

    def get_sha1_hash(self):
        if not self.latest_url:
            self.get_latest()
        
        sha1_url = f'{self.latest_url}.sha1'
        response = self.session.get(sha1_url)
        self.latest_sha1 = response.text.split()[0]
        return self.latest_sha1
