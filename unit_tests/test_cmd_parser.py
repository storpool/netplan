# Copyright (c) 2018  StorPool.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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
import subprocess
import sys
import unittest
import yaml

import ddt


def run_parser(args):
    """
    Run the netplan-parser utility with the specified command-line
    arguments and return its exit code and output.
    """
    env = {k: v for (k, v) in os.environ.items()}
    env['PYTHONPATH'] = ':'.join(sys.path)
    cmd = [sys.executable, '--', 'bin/netplan-parser.py'] + args
    proc = subprocess.Popen(cmd, env=env,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = proc.communicate()
    res = proc.wait()
    return (res, out[0].decode(encoding='US-ASCII'))


@ddt.ddt
class TestCmdNetPlanParser(unittest.TestCase):
    """
    Test the netplan-parser command-line utility.
    """
    @ddt.data(
        ('--help',
         '^usage:'),
        ('--version',
         '^netplan-parser [0-9a-z.]+\n$'),
        ('--features',
         '^Features:.* netplan-parser=[0-9a-z.]+( [^\n]+)?\n$'),
    )
    @ddt.unpack
    def test_queries(self, option, regex):
        """
        Make sure `netplan-parser --help` exits with code 0 and outputs
        a string starting with "usage:".
        Make sure `netplan-parser --version` exits with code 0 and outputs
        a single line that somewhat resembles a version number.
        Make sure `netplan-parser --features` exits with code 0 and outputs
        a single line that somewhat resembles a list of features.
        """
        (code, output) = run_parser([option])
        self.assertEqual(code, 0)
        self.assertRegexpMatches(output, regex)

    @ddt.data(
        ('test_data/override',
         'eno1'),
        ('test_data/full-9000',
         'br-enp4s0 eno1 enp2s0 enp2s0.617 enp2s0d1 enp4s0'),
        ('test_data/full-9002',
         'br-enp4s0 eno1 enp2s0 enp2s0.617 enp2s0d1 enp4s0'),
    )
    @ddt.unpack
    def test_output(self, root, names):
        """
        Test the actual output of the netplan-parser tool.
        """
        (code, output) = run_parser(['-f', 'names', '-r', root,
                                     'show'])
        self.assertEqual(code, 0)
        lines = output.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], names)
        self.assertEqual(lines[1], '')

        (code, output) = run_parser(['-f', 'yaml', '-r', root,
                                     'show'])
        self.assertEqual(code, 0)
        data = yaml.load(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)

        (code, output) = run_parser(['-f', 'json', '-r', root,
                                     'show'])
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)
