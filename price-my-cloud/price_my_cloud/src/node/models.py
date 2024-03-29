import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel
from decimal import Decimal

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
    time_of_processing = models.DurationField(null=True)

    def __str__(self):
        return self.name


class ComponentType(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class Component(TimeStampedModel):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    type = models.ForeignKey(ComponentType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    duration_of_operating = models.DurationField(default=TIMEDELTA_100_MS)
    hidden = models.BooleanField(default=True)
    cpu_utilization = models.DecimalField(
        null=True,
        max_digits=6,
        decimal_places=3,
        default=Decimal(0),
        validators=PERCENTAGE_VALIDATOR,
    )
    instance_type = models.CharField(max_length=255, null=True)

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
    packets = models.PositiveBigIntegerField()
    bytes = models.PositiveBigIntegerField()
    action = models.CharField(choices=as_choices(enums.FlowLogsAction), max_length=64)
    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        unique_together = ("from_component", "to_component", "action")

    def __str__(self):
        return f"From {self.from_component} to {self.to_component}"


class InstanceCost(TimeStampedModel):
    instance_type = models.CharField(max_length=255)
    cost_per_hour = models.DecimalField(
        max_digits=7, decimal_places=4, default=Decimal(0)
    )

    def __str__(self):
        return f"{self.instance_type}: {self.cost_per_hour}$"
