from django.contrib import admin
from node import models as node_models


class NodeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "created",
    )
    search_fields = (
        "name",
        "slug",
    )


class ComponentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created",
    )
    search_fields = ("name",)


class ComponentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "node",
        "type",
        "duration_of_operating",
    )
    search_fields = (
        "name",
        "node",
        "type",
    )


class ConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "from_component",
        "node",
        "to_component",
        "number_of_requests",
        "avg_time_of_request",
        "description",
    )
    search_fields = (
        "from_component",
        "from_component__id",
        "to_component",
        "to_component__id",
    )
    raw_id_fields = (
        "from_component",
        "to_component",
    )
    list_filter = ("from_component__node",)

    def node(self, object):
        return object.from_component.node


class InstanceCostAdmin(admin.ModelAdmin):
    list_display = (
        "instance_type",
        "cost_per_hour",
    )
    search_fields = ("instance_type",)


admin.site.register(node_models.Node, NodeAdmin)
admin.site.register(node_models.ComponentType, ComponentTypeAdmin)
admin.site.register(node_models.Component, ComponentAdmin)
admin.site.register(node_models.Connection, ConnectionAdmin)
admin.site.register(node_models.InstanceCost, InstanceCostAdmin)
