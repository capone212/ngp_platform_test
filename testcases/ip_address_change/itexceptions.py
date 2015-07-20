

class ItBaseException(RuntimeError):
    pass

class ItGeneralError(ItBaseException):
    pass

class ItCriticalError(ItBaseException):
    pass