'''
pyATS Library Sample Job File
'''
import os
from sys import platform

from genie.harness.main import gRun

if platform == "darwin":
    os.environ["NO_PROXY"] = os.environ.get("NO_PROXY", "novalue")


def main():
    test_path = os.path.dirname(os.path.abspath(__file__))

    gRun(subsection_datafile=f"{test_path}/subsection_datafile.yml",
         testbed=f"{test_path}/testbed.yml")
