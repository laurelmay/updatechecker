import abc
import json


class BaseUpdateChecker(metaclass=abc.ABCMeta):
    """
    Provides information about the latest version of a software.

    :type context: dict
    :param context: The global context object

    :type session: requests.Session
    :param session: The requests session to use for queries

    :type beta: bool
    :param beta: Whether or not to check for a beta version
    """

    @property
    @abc.abstractmethod
    def name(self):
        """
        The name of this software.

        This should be overriden as a class attribute.
        """
        pass

    @property
    @abc.abstractmethod
    def short_name(self):
        """
        The short name of the software.

        This should be overriden as a class attribute and should conform to:
          ^[a-z][a-z-]*[a-z]$
        """

    def __init__(self, context, session, beta=False):
        self.context = context
        self.session = session
        self._latest_version = None
        self._latest_url = None
        self._sha1_hash = None
        self.beta = beta
        self.loaded = False

    def load(self, force_reload=False):
        """
        Load the data about the latest version.

        This is handled outside `init` to allow for potential optimization
        opportunities.

        :param bool force_reload: Force a reload, even if already loaded
        """
        if self.loaded and not force_reload:
            return

        self._load()
        self.loaded = True

    @abc.abstractmethod
    def _load(self):
        """
        Load implementation to be overriden by implementing classes.
        """
        pass

    @property
    def latest_version(self):
        """
        Provide the latest version of the software.
        """
        return self._latest_version

    @property
    def latest_url(self):
        """
        Provide the URL of the latest version.
        """
        return self._latest_url

    @property
    def sha1_hash(self):
        """
        Provide the SHA1 hash of the latest version.
        """
        return self._sha1_hash


class BaseUpdateCheckerEncoder(json.JSONEncoder):
    def default(self, o):
        if not isinstance(o, BaseUpdateChecker):
            json.JSONEncoder.default(self, o)

        o.load()

        encoding = {
            "software": o.name,
            "latest": {
                "version": o.latest_version,
                "url": o.latest_url,
                "sha1": o.sha1_hash,
                "beta": bool(o.beta),
            },
        }
        return encoding
