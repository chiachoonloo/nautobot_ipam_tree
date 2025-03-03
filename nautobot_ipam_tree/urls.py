from django.urls import path
from .views import NodeChainView, PrefixChildrenView, StartView

urlpatterns = [
    path("api/node-chain/", NodeChainView.as_view(), name="node-chain"),
    path("api/node-chain/<uuid:prefix_id>", NodeChainView.as_view(), name="node-chain"),
    path("api/prefix-children/<uuid:prefix_id>", PrefixChildrenView.as_view(), name="prefix-children"),

    path("start", StartView.as_view(), name="start")
]
