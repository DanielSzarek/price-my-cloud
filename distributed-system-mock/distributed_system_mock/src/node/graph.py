from django.db.models import Count, Sum, Avg, F, DurationField
from graphviz import Digraph

from node import models as node_models
from aws.enums import FlowLogsAction
from node.utils import convert_bytes

TOTAL_REQUESTS_WARNING = 10
TOTAL_REQUESTS_CRITICAL = 20
TOTAL_PACKETS_WARNING = 1000
TOTAL_PACKETS_CRITICAL = 1500


class NodeGraph:
    def __init__(self, node: node_models.Node):
        self.node = node
        self.graph_nodes = node.component_set.filter(hidden=False)
        self.graph_edges_accepted = node_models.Connection.objects.filter(
            from_component__node=node,
            from_component__hidden=False,
            to_component__hidden=False,
            action=FlowLogsAction.ACCEPT.value,
        )
        self.graph_edges_rejected = node_models.Connection.objects.filter(
            from_component__node=node,
            from_component__hidden=False,
            to_component__hidden=False,
            action=FlowLogsAction.REJECT.value,
        )

    def get_component_color(self, total_requests, total_packets):
        if (total_requests >= TOTAL_REQUESTS_CRITICAL) or (
            total_packets >= TOTAL_PACKETS_CRITICAL
        ):
            return "red2"
        elif (total_requests >= TOTAL_REQUESTS_WARNING) or (
            total_packets >= TOTAL_PACKETS_WARNING
        ):
            return "orange"
        return "lightgreen"

    def get_svg_graph(self):
        dot = Digraph("node-graph", format="svg", comment="Node graph")
        dot.attr("node", fontname="Courier New", fontsize="13", margin="0.4")
        dot.attr(
            "edge", fontname="Courier", fontsize="11", arrowhead="vee", arrowsize="1"
        )
        dot.attr("node", shape="box")
        dot.node_attr.update(color="lightblue2", style="filled")

        for component in self.graph_nodes:
            aggregation = component.to_components.aggregate(
                total=Sum("number_of_requests"),
                packets=Sum("packets"),
                bytes=Sum("bytes"),
            )
            total_requests = aggregation["total"] or 0
            total_packets = aggregation["packets"] or 0
            total_bytes = convert_bytes(aggregation["bytes"] or 0)
            label = f"<<B>{component.name}</B><br/>Total received: {total_requests}<br/>Packets: {total_packets}<br/>Bytes: {total_bytes}>"
            dot.node(
                str(component.id),
                label=label,
                color=self.get_component_color(total_requests, total_packets),
                shape=None,
                href=self._prepare_component_edit_url(component),
                tooltip=str(component.id),
            )

        for connection in self.graph_edges_accepted:
            label = f"x{connection.number_of_requests} ({connection.packets} packets [{convert_bytes(connection.bytes)}])"
            dot.edge(
                str(connection.from_component.id),
                str(connection.to_component.id),
                label=label,
            )
        for connection in self.graph_edges_rejected:
            label = f"x{connection.number_of_requests} ({connection.packets} packets [{convert_bytes(connection.bytes)}])"
            dot.edge(
                str(connection.from_component.id),
                str(connection.to_component.id),
                label=label,
                color="red",
                fontcolor="red",
            )
        return dot.pipe().decode("utf-8")

    @staticmethod
    def _prepare_component_edit_url(component: node_models.Component) -> str:
        return f"/admin/node/component/{component.id}/change"
