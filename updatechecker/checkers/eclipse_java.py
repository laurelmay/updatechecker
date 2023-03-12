import json
import xml.etree.ElementTree as ET

import aiohttp

from updatechecker import checker

RELEASE_BASE_URL = "https://download.eclipse.org/technology/epp/downloads/release"
RELEASE_FILE = f"{RELEASE_BASE_URL}/release.xml"


class EclipseDataParsingError(Exception):
    def __init__(self, url, message):
        super().__init__(f"Unable to parse {url}: {message}")
        self.url = url


class EcliseReleaseFetchError(Exception):
    def __init__(self, release_names: list[str], errors: list[Exception]):
        releases = ", ".join(release_names)
        details = "\n".join([str(error) for error in errors])
        message = f"None of {releases} could be downloaded:\n{details}"
        super().__init__(message)
        self.release_names = release_names
        self.errors = errors


def candidate_versions(version_data: ET.Element, beta: bool) -> list[str]:
    if beta and (future := version_data.find('future')):
        return [future.text] if future.text else []
    # Sometimes the `release.xml` file does this really annoying thing just before a release
    # where `present` points to a totally invalid URL because it's set to `YYYY-MM/R` when
    # that doesn't exist yet (just `YYYY-MM/RC#`). So we'll grab `present` and hope that works
    # but we'll also check the last `past` release in the list (which should be the newest
    # stable release available).
    present = version_data.find('present')
    last = version_data.findall('past')[-1]
    candidates = [present, last]
    version_texts = [field.text for field in candidates if field.text]
    return version_texts


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
        versions = candidate_versions(version_data, self.beta)
        if not versions:
            raise EclipseDataParsingError(RELEASE_FILE, f"No valid version data")

        errors = []
        for version in versions:
            [release_name, release_type] = version.split('/')
            download_url = f"{RELEASE_BASE_URL}/{version}/eclipse-java-{release_name}-{release_type}-linux-gtk-{self.arch}.tar.gz"
            sha_url = f"{download_url}.sha1"
            try:
                async with self.session.get(sha_url) as sha_hash_request:
                    sha_hash = await sha_hash_request.text('utf-8')
                self._latest_url = download_url
                self._latest_version = release_name
                self._sha1_hash = sha_hash.split()[0]
                return
            except aiohttp.ClientResponseError as e:
                errors.append(e)
        if errors:
            raise EcliseReleaseFetchError(versions, errors)


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
