import abc


class BaseUpdateChecker(metaclass=abc.ABCMeta):
    def __init__(self, context, session):
        self.context = context
        self.session = session

    @abc.abstractmethod
    def get_latest(self):
        pass
