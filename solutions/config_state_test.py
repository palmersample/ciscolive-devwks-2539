# pylint: disable=too-many-arguments, too-many-positional-arguments
"""
pyATS Configuration State Testing Trigger solutions file

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

# Import JSON for formatted output
import json

# pyATS import
from genie.harness.base import Trigger
from pyats import aetest

# Set up logging
logger = logging.getLogger(__name__)


class TestOspfConfigState(Trigger):
    """
    OSPF Configuration state trigger
    """
    @aetest.setup
    def prepare_test(self, uut):
        """
        Perform setup tasks for this testscript.

        Tasks performed:
          - Use Genie Learn to collect the running configuration
          - Set a parameter named "running_config" to store the learned data

        :param uut: Testbed device object for this trigger
        :return: None
        """
        # Learn the device running-config and make it accessible to every test:
        device_config = uut.learn("config")
        self.parameters.update(running_config=device_config)

    @aetest.test
    def test_ospf_process_configured(self,
                                     running_config,
                                     ospf_process_id):
        """
        Test that the desired OSPF process is configured on the device. Given
        the learned running-config object, get the dictionary value for
        "running_config.get("router ospf {ospf_process_id}"

        If the result is not an empty dict, the test passes and a new
        parameter is created, named "ospf_config". Otherwise, fail
        the test.

        :param running_config: Genie-learned device configuration
        :param ospf_process_id: Trigger parameter for desired OSPF process ID
        :return: None
        """
        # Arrange: prepare the configuration line to match

        # router ospf <pid>
        expected_config_section = f"router ospf {ospf_process_id}"
        logger.info("Testing for '%s'", expected_config_section)

        # Get the configuration section
        ospf_config = running_config.get(expected_config_section, None)
        logger.info("OSPF Configuration:\n%s",
                    json.dumps(ospf_config, indent=2))

        # Assert: test that the configuration line exists
        assert ospf_config is not None, \
            "OSPF process not configured"

        # Cleanup: Create a parameter for the next test
        self.parameters.update(ospf_config=ospf_config)

    @aetest.test
    def test_ospf_router_id_configured(self,
                                       ospf_router_id,
                                       ospf_config=()):
        """
        Test that the desired OSPF router ID is configured on the device.

        :param ospf_router_id: Desired router-id from the trigger datafile
        :param ospf_config: Learned OSPF config from
            test_ospf_process_configured. If no config was learned, default
            to an empty tuple (()).
        :return: None
        """
        # Create the config line to test:
        # router-id <rid>
        router_id_line = f"router-id {ospf_router_id}"

        logger.info("Testing for '%s'", router_id_line)

        # Assert: test the router-id config exists
        assert router_id_line in ospf_config, \
            f"Expected config '{router_id_line}' not present"

    @aetest.test
    def test_ospf_tunnel_interface_config(self,
                                          steps,
                                          running_config,
                                          tunnel_interface,
                                          ospf_process_id,
                                          tunnel_ospf_area,
                                          tunnel_interface_enabled):
        """
        Test that the tunnel interface is configured as follows:
          - "ip ospf <ospf_process_id> area <tunnel_ospf_area>"
          - "shutdown" or "no shutdown", depending on the value of parameter
            "tunnel_interface_enabled"

        This test will fail if the Tunnel interface is enabled, because
        the default for Cisco IOS XE Software is to show "shutdown". The
        actual configured state is visible if "show running-config all" is
        executed, but that's not the case with the pyATS Learn feature.

        :param steps: aetest built-in "steps" class to group test results.
        :param running_config: Genie-learned device configuration
        :param tunnel_interface: Datafile parameter for the tunnel interface
        :param ospf_process_id: Datafile parameter value for OSPF PID
        :param tunnel_ospf_area: Datafile parameter for Tunnel OSPF area
        :param tunnel_interface_enabled: Datafile parameter for Tunnel
            interface state. True = "no shutdown", False = "shutdown".
        :return: None
        """

        # interface TunnelN
        expected_config_section = f"interface {tunnel_interface}"

        # ip ospf 4 area 0
        ospf_area_config_line = f"ip ospf {ospf_process_id} area {tunnel_ospf_area}"

        if tunnel_interface_enabled:
            # no shutdown
            interface_state_config_line = "no shutdown"
        else:
            # shutdown
            interface_state_config_line = "shutdown"

        # Get the interface configuration section
        interface_config = running_config.get(expected_config_section, {})
        logger.info("Interface Configuration:\n%s",
                    json.dumps(interface_config, indent=2))

        with steps.start("OSPF Area"):
            logger.info("Testing for '%s'", ospf_area_config_line)
            assert ospf_area_config_line in interface_config, \
                f"Expected config '{ospf_area_config_line}' not present"

        with steps.start("Interface state"):
            logger.info("Testing for '%s'", interface_state_config_line)
            assert interface_state_config_line in interface_config, \
                f"Expected config '{interface_state_config_line}' not present"

    @aetest.cleanup
    def test_cleanup(self):
        """
        Example cleanup method for this testscript. Nothing is performed here.

        :return: None
        """
        # Nothing is being performed, but the cleanup section will be executed
        # at the end of the test
        logger.info("All tests for this device have completed.")
