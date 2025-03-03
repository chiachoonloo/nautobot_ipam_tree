from nautobot.apps.ui import NavMenuGroup, NavMenuItem, NavMenuTab

# menu integration
menu_items = [
    NavMenuTab(
        name="IPAM",
        groups=(
            NavMenuGroup(
                name="IPAM Tree",
                weight=1,
                items=(
                    NavMenuItem(
                        name="🌳 Start Here 🌳",
                        link="plugins:nautobot_ipam_tree:start",
                        weight=1,
                    ),
                ),
            ),
        ),
    ),
]
