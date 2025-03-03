from nautobot.extras.plugins import NautobotAppConfig


class NautobotIPAMTreeConfig(NautobotAppConfig):
    name = "nautobot_ipam_tree"
    verbose_name = "Nautobot IPAM Tree"
    version = "0.1"
    base_url = "nautobot-ipam-tree"


config = NautobotIPAMTreeConfig
