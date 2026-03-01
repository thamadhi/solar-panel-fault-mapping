from abc import ABC, abstractmethod


class Preprocessor(ABC):

    @abstractmethod
    def preprocess(self, data):
        pass
