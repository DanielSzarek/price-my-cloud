from django.shortcuts import render
from django.views import View

from node import models as node_models
from node import graph as node_graph


class NodeGraphView(View):
    def get(self, request, *args, **kwargs):
        node = node_models.Node.objects.get(slug=kwargs.get("slug"))
        graph = node_graph.NodeGraph(node)
        return render(
            request,
            "node_graph.html",
            {"svg": graph.get_svg_graph, "nodes": graph.graph_nodes},
        )
