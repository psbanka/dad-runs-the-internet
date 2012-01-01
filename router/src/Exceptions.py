
class DriException(Exception):
    "A utility class for writing more exceptions"
    def __init__(self):
        Exception.__init__(self)
    def __repr__(self):
        return "ABSTRACT"
    def __str__(self):
        return self.__repr__()

class DownloadException(DriException):
    def __init__(self, url, output):
        self.url = url
        self.output = output
    def __repr__(self):
        return "DownloadException"

class UploadException(DriException):
    def __init__(self, url, output):
        self.url = url
        self.output = output
    def __repr__(self):
        return "UploadException"
