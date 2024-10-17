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
