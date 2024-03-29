from django.db.models import Sum
from graphviz import Digraph

from node import models as node_models
from aws.enums import FlowLogsAction
from node.utils import convert_bytes

CPU_UTILIZATION_WARNING = 40
CPU_UTILIZATION_CRITICAL = 70

NUMBER_OF_REQUESTS_PER_SECOND_WARNING = 1
NUMBER_OF_REQUESTS_PER_SECOND_CRITICAL = 1.5


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

    @staticmethod
    def get_component_color(cpu_utilization):
        if not cpu_utilization or cpu_utilization < CPU_UTILIZATION_WARNING:
            return "lightgreen"
        if cpu_utilization >= CPU_UTILIZATION_CRITICAL:
            return "red2"
        elif cpu_utilization >= CPU_UTILIZATION_WARNING:
            return "orange"

    def get_connection_thickness(self, number_of_requests):
        avg_connections_per_second = (
            number_of_requests / self.node.time_of_processing.seconds or 60
        )
        if avg_connections_per_second > NUMBER_OF_REQUESTS_PER_SECOND_CRITICAL:
            return "3.0"
        elif avg_connections_per_second > NUMBER_OF_REQUESTS_PER_SECOND_WARNING:
            return "1.5"
        return "0.75"

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
            cpu_utilization = component.cpu_utilization
            instance_type = component.instance_type or "Unknown type"
            duration = self.node.time_of_processing.seconds
            total_requests = aggregation["total"] or 0
            total_requests_per_second = (
                round(aggregation["total"] / duration, 2) if aggregation["total"] else 0
            )
            total_packets = aggregation["packets"] or 0
            total_packets_per_second = (
                round(aggregation["packets"] / duration, 2)
                if aggregation["total"]
                else 0
            )
            total_bytes = convert_bytes(aggregation["bytes"] or 0)
            total_bytes_per_second = (
                convert_bytes(round(aggregation["bytes"] / duration, 2))
                if aggregation["total"]
                else 0
            )

            label = (
                f"<<B>{component.name}</B><br/>--- {component.type} ---<br/><br/>"
                f"Total received: {total_requests} ({total_requests_per_second}/s)<br/>"
                f"Packets: {total_packets} ({total_packets_per_second}/s)<br/>"
                f"Bytes: {total_bytes} ({total_bytes_per_second}/s)<br/>"
                f"CPU utilization: {cpu_utilization}%<br/><br/>[{instance_type}]>"
            )
            dot.node(
                str(component.id),
                label=label,
                color=self.get_component_color(cpu_utilization),
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
                penwidth=self.get_connection_thickness(connection.number_of_requests),
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
