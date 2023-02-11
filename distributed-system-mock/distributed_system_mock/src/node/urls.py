from django.urls import path

from node.views import NodeGraphView

urlpatterns = [path("node-graph/<str:slug>/", NodeGraphView.as_view())]
