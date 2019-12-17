import abc


class BaseUpdateChecker(metaclass=abc.ABCMeta):
    def __init__(self, context, session):
        self.context = context
        self.session = session
        self.latest_url = None
        self.latest_sha1 = None

    @abc.abstractmethod
    def get_latest(self, beta=False):
        pass

    @abc.abstractmethod
    def get_sha1_hash(self):
        pass
