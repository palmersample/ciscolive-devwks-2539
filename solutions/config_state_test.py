import logging

# pyATS import
from genie.harness.base import Trigger
from pyats import aetest

# Import JSON for formatted output
import json

# Set up logging
logger = logging.getLogger(__name__)


class TestOspfConfigState(Trigger):
    @aetest.setup
    def prepare_test(self, uut):
        # Learn the device running-config and make it accessible to every test:
        device_config = uut.learn("config")
        self.parameters.update(running_config=device_config)

    @aetest.test
    def test_ospf_process_configured(self,
                                     running_config,
                                     ospf_process_id):
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
        # Nothing is being performed, but the cleanup section will be executed
        # at the end of the test
        logger.info("All tests for this device have completed.")
