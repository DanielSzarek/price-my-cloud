from django.contrib import admin
from aws import models as aws_models


class FlowLogAdmin(admin.ModelAdmin):
    list_display = (
        "node",
        "filename",
        "created",
    )
    search_fields = (
        "node__id",
        "node__name",
        "filename",
    )


class FlowLogDataAdmin(admin.ModelAdmin):
    list_display = (
        "flow_log",
        "source",
        "source_port",
        "destination",
        "destination_port",
        "protocol",
    )
    search_fields = (
        "node__id",
        "node__name",
        "filename",
    )


admin.site.register(aws_models.FlowLog, FlowLogAdmin)
admin.site.register(aws_models.FlowLogData, FlowLogDataAdmin)
