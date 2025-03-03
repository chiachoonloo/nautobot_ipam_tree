# nautobot_ipam_tree
Nautobot App to insert jsTree for IPAM Navigation

Hi, this repo is for learning only.

The motivation came about because some of our engineers are looking for a tree-style navigation for Prefixes objects.
the css/icons/jstree are all linked from internet in the templates.

  - There is a start link in the IPAM section, this will link to the first Prefix object in "Global" namespace
  - A Tree will should up on the left side of the Prefix details page
    - A namespace + ipv4/6 dropdown is available for further filtering
    - Open/Close of branches are done by clicking the icon
    - Clicking the text send you to the Prefix detail page, on page load, the Tree will call ajax+api to auto expand the tree to selected node
    - All the javascripts are in _tree.html template

There are some hardcode references that you should take note of:
views.py
	- uses ipaddress python module, needs installation
	- class StartView has a hardcode namespace name of "Global"
	- def _get_prefix_data (used by class PrefixChildrenView) has reference to prefix__role__name of "cust_transit/cust_routed"
		this only sets the icon, it is meant for my own customized usage

