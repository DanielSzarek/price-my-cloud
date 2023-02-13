from django.urls import path

from node import views as node_views

app_name = "nodes"

urlpatterns = [
    path("", node_views.Home.as_view(), name="home"),
    path("new-node/", node_views.NewNodeFileFieldFormView.as_view(), name="new-node"),
    path("node-graph/<str:slug>/", node_views.NodeGraphView.as_view(), name="graph"),
]
