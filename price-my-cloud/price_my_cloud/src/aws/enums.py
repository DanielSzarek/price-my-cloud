import enum


class FlowLogsAction(enum.Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class FlowLogsStatus(enum.Enum):
    OK = "OK"
    NODATA = "NODATA"
    SKIPDATA = "SKIPDATA"
