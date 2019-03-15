"""
Module contains project exceptions
"""


class ApiRosBaseError(Exception):
    """
    Base exception
    """
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LoginFailed(ApiRosBaseError):
    """
    Login failed exception
    """


class UnpackerException(ApiRosBaseError):
    pass


class BufferFull(UnpackerException):
    pass


class OutOfData(ApiRosBaseError):
    pass


class UnpackValueError(UnpackerException, ValueError):
    pass


class UnknownControlByteError(UnpackValueError):
    pass


class PackException(ApiRosBaseError):
    pass


class ParseException(ApiRosBaseError):
    pass
