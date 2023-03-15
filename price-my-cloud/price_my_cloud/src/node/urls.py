from django.urls import path

from node import views as node_views

app_name = "nodes"

urlpatterns = [
    path("", node_views.Home.as_view(), name="home"),
    path("new-node/", node_views.NodeCreationView.as_view(), name="new-node"),
    path(
        "node-details/<int:node_id>/",
        node_views.NodeDetailsView.as_view(),
        name="node-details",
    ),
    path("node-graph/<str:slug>/", node_views.NodeGraphView.as_view(), name="graph"),
    path(
        "component/<int:pk>/<int:node_id>/",
        node_views.ComponentFormUpdate.as_view(),
        name="component-update",
    ),
]
