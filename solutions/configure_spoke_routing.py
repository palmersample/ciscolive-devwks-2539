# pylint: disable=no-name-in-module
"""
pyATS Trigger to correct misconfiguration on the spoke router

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

# pyATS import
from genie.harness.base import Trigger
from pyats import aetest
from unicon.core.errors import SubCommandFailure


# Set up logging
logger = logging.getLogger(__name__)


class ConfigureSpokeOspf(Trigger):
    """
    pyATS Trigger class to configure the participant's spoke router for OSPF
    over the Tunnel interface. This script is provided for convenience and
    expedience when delivering a 45-minute workshop; the intent is to have
    tests fail and then succeed after running this trigger.
    """
    @aetest.test
    def configure_ospf_process(self, uut, ospf_process_id, ospf_router_id):
        """
        Configure the OSPF process using a Genie API

        :param uut: pyATS device object from the trigger datafile.
        :param ospf_process_id: Desired OSPF process ID (from datafile)
        :param ospf_router_id: Desired OSPF router ID (from datafile)
        :return: None
        """
        try:
            uut.api.configure_ospf_routing(ospf_process_id=ospf_process_id,
                                           router_id=ospf_router_id,
                                           router_config=True)
        except SubCommandFailure as err:
            self.failed(f"Could not configure OSPF process: {err}")

    @aetest.test
    def configure_ospf_default_passive(self, uut, ospf_process_id):
        """
        Configure OSPF process {ospf_process_id} to include
        "passive-interface default". This is the misconfiguration to be
        caught when the op state test fails during the workshop.

        :param uut: pyATS device object from the trigger datafile.
        :param ospf_process_id: Desired OSPF process ID (from datafile)
        :return: None
        """
        try:
            uut.api.configure_ospf_passive_interface(ospf_process_id=ospf_process_id,
                                                     interface="default")
        except SubCommandFailure as err:
            self.failed(f"Unable to configure passive-interface default: {err}")

    @aetest.test
    def configure_tunnel_ospf(self, uut, ospf_process_id, tunnel_interface, tunnel_ospf_area):
        """

        :param uut: pyATS device object from the trigger datafile.
        :param ospf_process_id: Desired OSPF process ID (from datafile)
        :param tunnel_interface: Tunnel interface to configure (from datafile)
        :param tunnel_ospf_area: Desired tunnel OSPF area (from datafile)
        :return: None
        """
        try:
            uut.api.configure_ospf_routing_on_interface(ospf_process_id=ospf_process_id,
                                                        interface=tunnel_interface,
                                                        areaid=tunnel_ospf_area)
        except SubCommandFailure as err:
            self.failed("Unable to configure OSPF routing on interface "
                        f"'{tunnel_interface}': {err}")

    @aetest.test
    def enable_tunnel_interface(self, uut, tunnel_interface):
        """

        :param uut: pyATS device object from the trigger datafile.
        :param tunnel_interface: Tunnel interface to configure (from datafile)
        :return: None
        """
        try:
            uut.api.unshut_interface(interface=tunnel_interface)
        except SubCommandFailure as err:
            self.failed(f"Unable to unshut interface '{tunnel_interface}': {err}")

    @aetest.test
    def configure_tunnel_not_passive(self, uut, ospf_process_id, tunnel_interface):
        """

        :param uut: pyATS device object from the trigger datafile.
        :param ospf_process_id: Desired OSPF process ID (from datafile)
        :param tunnel_interface: Tunnel interface to configure (from datafile)
        :return: None
        """
        try:
            uut.api.remove_ospf_passive_interface(ospf_process_id=ospf_process_id,
                                                  interface=tunnel_interface)
        except SubCommandFailure as err:
            self.failed(f"Unable to unconfigure passive-interface on '{tunnel_interface}': {err}")
