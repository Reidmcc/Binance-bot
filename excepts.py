##### Custom exceptions for pyBinance
#!/usr/bin/env python
# coding=utf-8


# Exceptions
class MalformedRequest(Exception):
    """ HTTP 4XX return codes are used for for malformed requests; the issue is on the sender's side. """

class StatusUnknown(Exception):
    """ HTTP 504 return code is used when the API successfully sent the message but not get a response within the timeout period. 
    It is important to NOT treat this as a failure; the execution status is UNKNOWN and could have been a success. """

class InternalError(Exception):
    """ HTTP 5XX return codes are used for internal errors; the issue is on Binance's side. """
