# Copyright (c) 2018, 2019  StorPool.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unit tests for the netplan-parser command-line utility.
"""

import os
import json
import re
import subprocess
import sys
import unittest

from typing import List, Tuple

import ddt
import yaml


_TYPING_USED = (List, Tuple)


def run_parser(args):
    # type: (List[str]) -> Tuple[int, str, str]
    """
    Run the netplan-parser utility with the specified command-line
    arguments and return its exit code and output.
    """
    env = dict(os.environ.items())
    env["PYTHONPATH"] = ":".join(sys.path)
    cmd = [sys.executable, "--", "bin/netplan-parser"] + args
    with subprocess.Popen(
        cmd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as proc:
        out = proc.communicate()
        res = proc.wait()
        return (
            res,
            out[0].decode(encoding="US-ASCII"),
            out[1].decode(encoding="utf-8"),
        )


@ddt.ddt
class TestCmdNetPlanParser(unittest.TestCase):
    # pylint: disable=no-self-use
    """
    Test the netplan-parser command-line utility.
    """

    @ddt.data(
        ("--help", "^usage:"),
        ("--version", "^netplan-parser [0-9a-z.]+\n$"),
        ("--features", "^Features:.* netplan-parser=[0-9a-z.]+( [^\n]+)?\n$"),
    )
    @ddt.unpack
    def test_queries(self, option, regex):
        # type: (TestCmdNetPlanParser, str, str) -> None
        """
        Make sure `netplan-parser --help` exits with code 0 and outputs
        a string starting with "usage:".
        Make sure `netplan-parser --version` exits with code 0 and outputs
        a single line that somewhat resembles a version number.
        Make sure `netplan-parser --features` exits with code 0 and outputs
        a single line that somewhat resembles a list of features.
        """
        (code, output, errs) = run_parser([option])
        assert errs == ""
        assert code == 0
        assert re.match(regex, output)

    @ddt.data(
        ("test_data/override", "eno1"),
        ("test_data/full-9000", "br-enp4s0 eno1 enp2s0 enp2s0.617 enp2s0d1 enp4s0"),
        ("test_data/full-9002", "br-enp4s0 eno1 enp2s0 enp2s0.617 enp2s0d1 enp4s0"),
    )
    @ddt.unpack
    def test_show(self, root, names):
        # type: (TestCmdNetPlanParser, str, str) -> None
        """
        Test "netplan-parser show".
        """
        (code, output, errs) = run_parser(["-f", "names", "-r", root, "show"])
        assert errs == ""
        assert code == 0
        lines = output.split("\n")
        assert len(lines) == 2
        assert lines[0] == names
        assert lines[1] == ""

        (code, output, errs) = run_parser(["-f", "yaml", "-r", root, "show"])
        assert errs == ""
        assert code == 0
        data = yaml.safe_load(output)
        assert isinstance(data, dict)
        assert " ".join(sorted(data.keys())) == names

        (code, output, errs) = run_parser(["-f", "json", "-r", root, "show"])
        assert errs == ""
        assert code == 0
        data = json.loads(output)
        assert isinstance(data, dict)
        assert " ".join(sorted(data.keys())) == names

    @ddt.data(
        ("test_data/override", "eno1", "eno1"),
        ("test_data/full-9000", "br-enp4s0", "br-enp4s0 enp4s0"),
        ("test_data/full-9002", "enp2s0.617 br-enp4s0", "br-enp4s0 enp2s0 enp2s0.617 enp4s0"),
    )
    @ddt.unpack
    def test_related(self, root, query, names):
        # type: (TestCmdNetPlanParser, str, str, str) -> None
        """
        Test "netplan-parser related".
        """
        query_split = query.split(" ")
        (code, output, errs) = run_parser(["-f", "names", "-r", root, "related"] + query_split)
        assert errs == ""
        assert code == 0
        lines = output.split("\n")
        assert len(lines) == 2
        assert lines[0] == names
        assert lines[1] == ""

        (code, output, errs) = run_parser(["-f", "yaml", "-r", root, "related"] + query_split)
        assert errs == ""
        assert code == 0
        data = yaml.safe_load(output)
        assert isinstance(data, dict)
        assert " ".join(sorted(data.keys())) == names

        (code, output, errs) = run_parser(["-f", "json", "-r", root, "related"] + query_split)
        assert errs == ""
        assert code == 0
        data = json.loads(output)
        assert isinstance(data, dict)
        assert " ".join(sorted(data.keys())) == names

    @ddt.data(
        ("test_data/override", "eno1", "eno1"),
        ("test_data/full-9000", "br-enp4s0", "enp4s0"),
        ("test_data/full-9002", "enp2s0.617 br-enp4s0", "enp2s0 enp4s0"),
    )
    @ddt.unpack
    def test_physical(self, root, query, names):
        # type: (TestCmdNetPlanParser, str, str, str) -> None
        """
        Test "netplan-parser physical".
        """
        query_split = query.split(" ")
        (code, output, errs) = run_parser(["-f", "names", "-r", root, "physical"] + query_split)
        assert errs == ""
        assert code == 0
        lines = output.split("\n")
        assert len(lines) == 2
        assert lines[0] == names
        assert lines[1] == ""

        (code, output, errs) = run_parser(["-f", "yaml", "-r", root, "physical"] + query_split)
        assert errs == ""
        assert code == 0
        data = yaml.safe_load(output)
        assert isinstance(data, dict)
        assert " ".join(sorted(data.keys())) == names

        (code, output, errs) = run_parser(["-f", "json", "-r", root, "physical"] + query_split)
        assert errs == ""
        assert code == 0
        data = json.loads(output)
        assert isinstance(data, dict)
        assert " ".join(sorted(data.keys())) == names

    def test_exclude(self):
        # type: (TestCmdNetPlanParser) -> None
        """
        Test "netplan-parser -x conffile show".
        """
        (code, output, errs) = run_parser(
            ["-f", "yaml", "-r", "test_data/full-9002", "show", "enp2s0"]
        )
        assert errs == ""
        assert code == 0
        data = yaml.safe_load(output)
        assert isinstance(data, dict)
        assert list(data.keys()) == ["enp2s0"]
        assert data["enp2s0"].get("mtu", 1500) == 9002

        (code, output, errs) = run_parser(
            ["-f", "yaml", "-r", "test_data/full-9002", "-x", "99-storpool.yaml", "show", "enp2s0"]
        )
        assert errs == ""
        assert code == 0
        data = yaml.safe_load(output)
        assert isinstance(data, dict)
        assert list(data.keys()) == ["enp2s0"]
        assert data["enp2s0"].get("mtu", 1500) == 9000
