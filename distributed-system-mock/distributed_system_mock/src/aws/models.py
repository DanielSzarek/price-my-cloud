from django.db import models
from django_extensions.db.models import TimeStampedModel

from aws import enums
from aws.enum_support import as_choices


class FlowLog(TimeStampedModel):
    node = models.ForeignKey("node.Node", on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.node} - {self.filename}"


class FlowLogData(TimeStampedModel):
    flow_log = models.ForeignKey("FlowLog", on_delete=models.CASCADE)
    source = models.GenericIPAddressField()
    destination = models.GenericIPAddressField()
    source_port = models.PositiveIntegerField()
    destination_port = models.PositiveIntegerField()
    protocol = models.PositiveIntegerField()
    packet = models.PositiveIntegerField()
    bytes = models.PositiveIntegerField()
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    action = models.CharField(choices=as_choices(enums.FlowLogsAction), max_length=255)
    log_status = models.CharField(
        choices=as_choices(enums.FlowLogsStatus), max_length=255
    )

    def __str__(self):
        return f"{self.source}:{self.source_port} -> {self.destination}:{self.destination_port}"
