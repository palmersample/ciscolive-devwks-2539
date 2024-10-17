import logging

# pyATS import
from genie.harness.base import Trigger
from pyats import aetest
from genie.metaparser.util.exceptions import SchemaEmptyParserError, InvalidCommandError
from unicon.core.errors import SubCommandFailure

import json
import ipaddress

# Set up logging
logger = logging.getLogger(__name__)


class ConfigureSpokeOspf(Trigger):
    @aetest.test
    def configure_ospf_process(self, uut, ospf_process_id, ospf_router_id):
        try:
            uut.api.configure_ospf_routing(ospf_process_id=ospf_process_id,
                                           router_id=ospf_router_id,
                                           router_config=True)
        except SubCommandFailure as err:
            self.failed(f"Could not configure OSPF process: {err}")

    @aetest.test
    def configure_ospf_default_passive(self, uut, ospf_process_id):
        try:
            uut.api.configure_ospf_passive_interface(ospf_process_id=ospf_process_id,
                                                     interface="default")
        except SubCommandFailure as err:
            self.failed(f"Unable to configure passive-interface default: {err}")

    @aetest.test
    def configure_tunnel_ospf(self, uut, ospf_process_id, tunnel_interface, tunnel_ospf_area):
        try:
            uut.api.configure_ospf_routing_on_interface(ospf_process_id=ospf_process_id,
                                                        interface=tunnel_interface,
                                                        areaid=tunnel_ospf_area)
        except SubCommandFailure as err:
            self.failed(f"Unable to configure OSPF routing on interface '{tunnel_interface}': {err}")

    @aetest.test
    def enable_tunnel_interface(self, uut, tunnel_interface):
        try:
            uut.api.unshut_interface(interface=tunnel_interface)
        except SubCommandFailure as err:
            self.failed(f"Unable to unshut interface '{tunnel_interface}': {err}")

    @aetest.test
    def configure_tunnel_not_passive(self, uut, ospf_process_id, tunnel_interface):
        try:
            uut.api.remove_ospf_passive_interface(ospf_process_id=ospf_process_id,
                                                  interface=tunnel_interface)
        except SubCommandFailure as err:
            self.failed(f"Unable to unconfigure passive-interface on '{tunnel_interface}': {err}")
