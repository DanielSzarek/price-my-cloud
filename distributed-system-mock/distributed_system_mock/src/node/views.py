from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views import View

from aws import utils as aws_utils
from node import models as node_models
from node import graph as node_graph

from django.shortcuts import render

from django.views.generic.edit import FormView
from node import forms as node_forms
from bootstrap_modal_forms.generic import BSModalUpdateView


class Home(View):
    def get(self, request, *args, **kwargs):
        nodes = node_models.Node.objects.all()
        return render(
            request,
            "home.html",
            {
                "nodes": nodes,
            },
        )


class NodeCreationView(FormView):
    form_class = node_forms.NodeCreationForm
    template_name = "new_node.html"
    success_url = reverse_lazy("nodes:home")

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist("file_field")
        if form.is_valid():
            node = node_models.Node.objects.create(
                name=form.cleaned_data["node_name"],
                slug=slugify(form.cleaned_data["node_name"]),
            )
            for file in files:
                aws_utils.handle_uploaded_file(node, file)
            aws_utils.convert_flow_logs_to_components(node)
            return self.form_valid(form)
        return self.form_invalid(form)


class NodeDetailsView(View):
    def get(self, request, *args, **kwargs):
        node = node_models.Node.objects.get(id=kwargs.get("node_id"))
        components_shown = node.component_set.filter(hidden=False).order_by("name")
        components_hidden = node.component_set.filter(hidden=True).order_by("name")

        return render(
            request,
            "node_details.html",
            {
                "node": node,
                "components_shown": components_shown,
                "components_hidden": components_hidden,
            },
        )


class NodeGraphView(View):
    def get(self, request, *args, **kwargs):
        node = node_models.Node.objects.get(slug=kwargs.get("slug"))
        graph = node_graph.NodeGraph(node)
        return render(
            request,
            "node_graph.html",
            {
                "node": node,
                "svg": graph.get_svg_graph,
            },
        )


class ComponentFormUpdate(BSModalUpdateView):
    model = node_models.Component
    template_name = "forms/component_update_form.html"
    form_class = node_forms.ComponentModelForm
    success_message = "Component has been saved"

    def get_success_url(self):
        return reverse_lazy(
            "nodes:node-details", kwargs={"node_id": str(self.kwargs["node_id"])}
        )
