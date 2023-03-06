import datetime

from django.db import models
from django_extensions.db.models import TimeStampedModel

from aws import enums
from aws.enum_support import as_choices

TIMEDELTA_100_MS = datetime.timedelta(milliseconds=100)


class Node(TimeStampedModel):
    name = models.CharField(
        max_length=255,
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.name


class ComponentType(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Component(TimeStampedModel):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    duration_of_operating = models.DurationField(default=TIMEDELTA_100_MS)
    hidden = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            "node",
            "name",
        )

    def __str__(self):
        return f"{self.name} ({self.type.name})"


class Connection(TimeStampedModel):
    from_component = models.ForeignKey(
        Component, related_name="from_components", on_delete=models.CASCADE
    )
    to_component = models.ForeignKey(
        Component, related_name="to_components", on_delete=models.CASCADE
    )
    number_of_requests = models.PositiveIntegerField()
    avg_time_of_request = models.DurationField(default=TIMEDELTA_100_MS)
    description = models.CharField(max_length=255, null=True)
    packets = models.PositiveIntegerField()
    bytes = models.PositiveBigIntegerField()
    action = models.CharField(choices=as_choices(enums.FlowLogsAction), max_length=64)

    class Meta:
        unique_together = ("from_component", "to_component", "action")

    def __str__(self):
        return f"From {self.from_component} to {self.to_component}"
