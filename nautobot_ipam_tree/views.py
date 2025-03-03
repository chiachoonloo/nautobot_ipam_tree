from ipaddress import ip_network
from django.urls import reverse
from urllib.parse import urlencode
from django.views.generic import TemplateView
from nautobot.ipam.models import Prefix, Namespace
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from nautobot.ipam.views import PrefixView as IPAMPrefixView


# prefix with tree
class PrefixViewWithTree(IPAMPrefixView):
    """
        This custom view subclass original IPAM's Prefix View, we then tell it to use our template
        Our template contains original block.super, and our tree
    """

    def get_template_name(self):
        return ["nautobot_ipam_tree/prefix_with_tree.html"]

    def get_extra_context(self, *args, **kwargs):
        context = super().get_extra_context(*args, **kwargs)

        namespaces = []
        for nb_namespace in Namespace.objects.all():
            if nb_prefix := Prefix.objects.filter(namespace=nb_namespace).first():
                namespaces.append({"name": nb_namespace.name, "href": nb_prefix.get_absolute_url()})
        context["select_namespaces"] = namespaces

        object = args[1]  # request, instance from Nautobot's Core::Views::Generic::ObjectView
        versions = []
        for i in [4, 6]:
            t = Prefix.objects.filter(namespace=object.namespace, ip_version=i).first()
            versions.append({"version": i, "href": t.get_absolute_url() if t else ""})
        context["select_versions"] = versions

        return context


# api for retrieving prefix parents / node chain
class NodeChainView(APIView):
    def get_queryset(self):
        return Prefix.objects

    def get(self, requests, **kwargs):
        _ = requests
        prefix_id = kwargs.get("prefix_id")
        if not prefix_id:
            return Response([], status=status.HTTP_200_OK)

        nb_prefix = self.get_queryset().filter(id=prefix_id).first()
        chain = []

        # loop nb_prefix and move step up to parent, inserting id into chain
        while nb_prefix:
            chain.insert(0, str(nb_prefix.id))
            if nb_prefix.parent:
                nb_prefix = nb_prefix.parent
            else:
                break

        if chain:
            return Response(chain, status=status.HTTP_200_OK)
        return Response({"error": f"Cannot find Prefix with id {prefix_id}"}, status=status.HTTP_400_BAD_REQUEST)


# api for retrieving children
class PrefixChildrenView(APIView):
    def get_queryset(self):
        return Prefix.objects

    def get(self, request, **kwargs):
        get_root = request.GET.get("root", False)
        prefix_id = kwargs.get("prefix_id")
        nb_prefix = self.get_queryset().filter(id=prefix_id).first()

        if not nb_prefix:
            return Response({"error": f"No Prefix with id {prefix_id}"}, status=status.HTTP_400_BAD_REQUEST)

        if get_root:
            qs = Prefix.objects.filter(
                parent__isnull=True,
                ip_version=nb_prefix.ip_version,
                namespace=nb_prefix.namespace,
            )
            data = [self._get_prefix_data(i) for i in qs]
            data = sorted(data, key=lambda i: ip_network(i["prefix"]))
            return Response(data, status=status.HTTP_200_OK)
        else:
            # nautobot records
            qs = Prefix.objects.filter(parent=nb_prefix)
            data = [self._get_prefix_data(i) for i in qs]

            # now we also add "available" prefixes in, but these are not real records
            for free in nb_prefix.get_available_prefixes().iter_cidrs():
                cidr = str(free)

                add_params = {"prefix": f"{cidr} <-- check", "namespace": str(nb_prefix.namespace.id)}
                add_url = f"{reverse('ipam:prefix_add')}?{urlencode(add_params)}"

                data.append({
                    "prefix": cidr,
                    "id": cidr,
                    "text": (
                        f"<span class='unused_ip' onclick=\"window.open('{add_url}', '_blank')\">"
                        f"{cidr} (add)"
                        "</span>"
                    ),
                    "children": False,
                    "icon": "bx bxs-leaf"
                })

            data = sorted(data, key=lambda i: ip_network(i["prefix"]))
            return Response(data, status=status.HTTP_200_OK)

    def _get_prefix_data(self, nb_prefix):
        util = nb_prefix.get_utilization()
        util_percent = round(util.numerator / util.denominator * 100)
        has_children = False if nb_prefix.is_leaf_node() else True

        default_icon = "bx bxs-folder"
        if has_children:
            icon = default_icon
        if nb_prefix.role and nb_prefix.role.name in ["cust_transit", "cust_routed"]:
            icon = "bx bx-body"
        elif not has_children:
            icon = "bx bx-radio-circle-marked"

        return {
            "prefix": str(nb_prefix),
            "id": str(nb_prefix.id),
            "text": (
                f"<span onclick=\"window.open('{nb_prefix.get_absolute_url()}', '_self')\">"
                f"{nb_prefix.prefix} ( {nb_prefix.location or 'no-site'} | {nb_prefix.role or 'no-role'} ) "
                f"{util_percent}%</span>"
            ),
            "children": has_children,
            "icon": icon,
        }


class StartView(TemplateView):
    template_name = "nautobot_ipam_tree/start.html"

    # django's Templateview, uses get_context_data
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        url = Prefix.objects.filter(namespace__name="Global", ip_version=4).first().get_absolute_url()
        context["start_url"] = url
        return context


# replace core views with my views
override_views = {
    "ipam:prefix": PrefixViewWithTree.as_view(),
}
