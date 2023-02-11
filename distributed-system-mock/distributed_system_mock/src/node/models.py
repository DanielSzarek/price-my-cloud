import datetime

from django.db import models
from django_extensions.db.models import TimeStampedModel

TIMEDELTA_100_MS = datetime.timedelta(milliseconds=100)


class Node(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)  # TODO change to slug field

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
    description = models.CharField(max_length=255)

    class Meta:
        # Let's suppose that we have only 1 connection mechanism now
        unique_together = ("from_component", "to_component")

    def __str__(self):
        return f"From {self.from_component} to {self.to_component}"
