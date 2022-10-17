from graphviz import Digraph

from node import models as node_models


class NodeGraph:
    def __init__(self, node: node_models.Node):
        self.node = node
        self.graph_nodes = node.component_set.all()
        self.graph_edges = node_models.Connection.objects.filter(
            from_component__node=node
        )

    def get_svg_graph(self):
        dot = Digraph("node-graph", format="svg", comment="Node graph")
        dot.attr("node", fontname="Courier New", fontsize="13", margin="0.4")
        dot.attr("edge", fontname="Courier", fontsize="11", arrowhead="none")
        dot.attr("node", shape="box")
        dot.node_attr.update(color="lightblue2", style="filled")

        for component in self.graph_nodes:
            label = f"<<B>{component.name}</B><br/>Operating time: {component.duration_of_operating}>"
            dot.node(
                str(component.id),
                label=label,
                color="lightblue2",
                shape=None,
                href=self._prepare_component_edit_url(component),
                tooltip=str(component.id),
            )

        for connection in self.graph_edges:
            label = f"{connection.description} ({connection.number_of_requests} x {connection.avg_time_of_request.total_seconds() * 1000} ms)"
            dot.edge(
                str(connection.from_component.id),
                str(connection.to_component.id),
                label=label,
            )
        return dot.pipe().decode("utf-8")

    @staticmethod
    def _prepare_component_edit_url(component: node_models.Component) -> str:
        return f"/admin/node/component/{component.id}/change"
