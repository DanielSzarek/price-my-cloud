from django.db import models
from django_extensions.db.models import TimeStampedModel

from aws import enums
from aws.migrations.enum_support import as_choices


class FlowLog(TimeStampedModel):
    filename = models.CharField(max_length=255)


class FlowLogData(TimeStampedModel):
    flow_log = models.ForeignKey("FlowLog", on_delete=models.CASCADE)
    source = models.GenericIPAddressField()
    destination = models.GenericIPAddressField()
    source_port = models.PositiveSmallIntegerField()
    destination_port = models.PositiveSmallIntegerField()
    protocol = models.PositiveSmallIntegerField()
    packet = models.PositiveIntegerField()
    bytes = models.PositiveIntegerField()
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    action = models.CharField(choices=as_choices(enums.FlowLogsAction))
    log_status = models.CharField(choices=as_choices(enums.FlowLogsStatus))
