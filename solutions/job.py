"""
pyATS Easypy job solutions file

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

import os

from genie.harness.main import gRun

def main():
    """
    Required method to instantiate the Easypy runtime environment for the test

    :return: None
    """
    test_path = os.path.dirname(os.path.abspath(__file__))

    gRun(subsection_datafile=f"{test_path}/subsection_datafile.yml",
         testbed=f"{test_path}/testbed.yml")
