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


class TestOspfOpState(Trigger):
    @aetest.test
    def test_ospf_router_id(self,
                            uut,
                            ospf_process_id,
                            ospf_router_id):

        logger.info("Testing OSPF process '%s' for router-id '%s'",
                    ospf_process_id,
                    ospf_router_id)

        # "instance" argument is expected to be a string
        ops_router_id = uut.api.get_ospf_router_id(instance=str(ospf_process_id))

        assert ospf_router_id == ops_router_id, \
            f"Expected: {ospf_router_id} - actual is: {ops_router_id}"

    @aetest.test
    def test_tunnel_ospf_area(self, uut, ospf_process_id, tunnel_interface, tunnel_ospf_area):

        logger.info("Testing interface '%s' is in OSPF area '%s'",
                    tunnel_interface,
                    tunnel_ospf_area)

        desired_ospf_area = str(ipaddress.IPv4Address(tunnel_ospf_area))
        try:
            ops_ospf_area = uut.api.get_ospf_area_of_interface(interface=tunnel_interface,
                                                               process_id=str(ospf_process_id))
        except (SubCommandFailure,
                InvalidCommandError,
                IndexError) as err:
            self.failed(f"Could not get OSPF area for interface '{tunnel_interface}': {err}")

        assert desired_ospf_area == ops_ospf_area, \
            f"Expected: {desired_ospf_area} - actual is: {ops_ospf_area}"

    @aetest.test
    def test_tunnel_interface_state(self, uut, steps, tunnel_interface, tunnel_interface_enabled):

        # Note: "show ip protocols" is a better reflection for passive interface,
        # but the parser needs to be updated to match Tunnel* in the regex.
        # Added to personal TODO -LPS

        try:
            interface_op_state = uut.parse(f"show ip ospf interface {tunnel_interface}")
        except (SubCommandFailure, InvalidCommandError) as err:
            self.failed(f"Could not parse OSPF data for interface '{tunnel_interface}': {err}")

        logger.info("Interface op state:\n%s", json.dumps(interface_op_state, indent=2))

        with steps.start("enabled", continue_=True):
            assert interface_op_state.q.contains_key_value("enable", tunnel_interface_enabled), \
                "Interface is shutdown"

        with steps.start("line protocol", continue_=True):
            assert interface_op_state.q.contains_key_value("line_protocol", tunnel_interface_enabled), \
                "Interface line protocol mismatch"

        with steps.start("passive"):
            assert interface_op_state.q.contains_key_value("passive", False), \
                "Interface is passive"
