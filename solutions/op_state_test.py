# pylint: disable=no-name-in-module
"""
pyATS Operational State Test Trigger solutions file

Developed for Cisco Live, DevNet Workshop DEVWKS-2539

Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Palmer Sample"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import logging

import json
import ipaddress

# pyATS import
from pyats import aetest
from genie.harness.base import Trigger
from genie.metaparser.util.exceptions import SchemaEmptyParserError, InvalidCommandError
from unicon.core.errors import SubCommandFailure

# Set up logging
logger = logging.getLogger(__name__)


class TestOspfOpState(Trigger):
    """
    OSPF operational state trigger
    """
    @aetest.test
    def test_ospf_router_id(self,
                            uut,
                            ospf_process_id,
                            ospf_router_id):
        """
        Use a Genie API to obtain the OSPF process router-id and test that
        it matches the desired state from the trigger datafile.

        :param uut: Testbed device object for this trigger
        :param ospf_process_id: Desired OSPF process ID (from datafile)
        :param ospf_router_id: Desired OSPF router ID (from datafile)
        :return: None
        """

        logger.info("Testing OSPF process '%s' for router-id '%s'",
                    ospf_process_id,
                    ospf_router_id)

        # "instance" argument is expected to be a string
        ops_router_id = uut.api.get_ospf_router_id(instance=str(ospf_process_id))

        assert ospf_router_id == ops_router_id, \
            f"Expected: {ospf_router_id} - actual is: {ops_router_id}"

    @aetest.test
    def test_tunnel_ospf_area(self, uut, ospf_process_id, tunnel_interface, tunnel_ospf_area):
        """

        :param uut: Testbed device object for this trigger
        :param ospf_process_id: Desired OSPF process ID (from datafile)
        :param tunnel_interface: Tunnel interface to configure (from datafile)
        :param tunnel_ospf_area: Desired tunnel OSPF area (from datafile)
        :return: None
        """

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
        """

        :param uut: Testbed device object for this trigger
        :param steps: aetest built-in "steps" class to group test results.
        :param tunnel_interface: Tunnel interface to configure (from datafile)
        :param tunnel_interface_enabled: Datafile parameter for Tunnel to match
            the op state (True = "up/up", False = "?/down")
        :return: None
        """

        # Note: "show ip protocols" is a better reflection for passive interface,
        # but the parser needs to be updated to match Tunnel* in the regex.
        # Added to personal TODO -LPS

        try:
            interface_op_state = uut.parse(f"show ip ospf interface {tunnel_interface}")
        except (SubCommandFailure,
                SchemaEmptyParserError,
                InvalidCommandError) as err:
            self.failed(f"Could not parse OSPF data for interface '{tunnel_interface}': {err}")

        logger.info("Interface op state:\n%s", json.dumps(interface_op_state, indent=2))

        with steps.start("enabled", continue_=True):
            assert interface_op_state.q.contains_key_value("enable",
                                                           tunnel_interface_enabled), \
                "Interface is shutdown"

        with steps.start("line protocol", continue_=True):
            assert interface_op_state.q.contains_key_value("line_protocol",
                                                           tunnel_interface_enabled), \
                "Interface line protocol mismatch"

        with steps.start("passive"):
            assert interface_op_state.q.contains_key_value("passive", False), \
                "Interface is passive"

    @aetest.test
    def test_hub_loopback_route_is_present(self, uut, hub_loopback_ip):
        """

        :param uut: Testbed device object for this trigger
        :param hub_loopback_ip: Expected hub Loopback IP address to be present
            in the global RIB
        :return: None
        """
        logger.info("Testing hub loopback IP '%s' is present in the routing table",
                    hub_loopback_ip)

        ospf_routes = uut.api.get_routing_ospf_routes()
        logger.info("OSPF routes present:\n%s", json.dumps(ospf_routes, indent=2))

        assert hub_loopback_ip in ospf_routes, \
            f"Expected route '{hub_loopback_ip}' not present in the spoke RIB."
