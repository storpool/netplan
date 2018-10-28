# Copyright (c) 2018  StorPool.
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
    env = {k: v for (k, v) in os.environ.items()}
    env['PYTHONPATH'] = ':'.join(sys.path)
    cmd = [sys.executable, '--', 'bin/netplan-parser'] + args
    proc = subprocess.Popen(cmd, env=env,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out = proc.communicate()
    res = proc.wait()
    return (res,
            out[0].decode(encoding='US-ASCII'),
            out[1].decode(encoding='utf-8'))


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
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        self.assertRegexpMatches(output, regex)  # pylint: disable=W1505

    @ddt.data(
        ('test_data/override',
         'eno1'),
        ('test_data/full-9000',
         'br-enp4s0 eno1 enp2s0 enp2s0.617 enp2s0d1 enp4s0'),
        ('test_data/full-9002',
         'br-enp4s0 eno1 enp2s0 enp2s0.617 enp2s0d1 enp4s0'),
    )
    @ddt.unpack
    def test_show(self, root, names):
        # type: (TestCmdNetPlanParser, str, str) -> None
        """
        Test "netplan-parser show".
        """
        (code, output, errs) = run_parser(['-f', 'names', '-r', root,
                                           'show'])
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        lines = output.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], names)
        self.assertEqual(lines[1], '')

        (code, output, errs) = run_parser(['-f', 'yaml', '-r', root,
                                           'show'])
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = yaml.load(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)

        (code, output, errs) = run_parser(['-f', 'json', '-r', root,
                                           'show'])
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)

    @ddt.data(
        ('test_data/override',
         'eno1',
         'eno1'),
        ('test_data/full-9000',
         'br-enp4s0',
         'br-enp4s0 enp4s0'),
        ('test_data/full-9002',
         'enp2s0.617 br-enp4s0',
         'br-enp4s0 enp2s0 enp2s0.617 enp4s0'),
    )
    @ddt.unpack
    def test_related(self, root, query, names):
        # type: (TestCmdNetPlanParser, str, str, str) -> None
        """
        Test "netplan-parser related".
        """
        query_split = query.split(' ')
        (code, output, errs) = run_parser(['-f', 'names', '-r', root,
                                           'related'] + query_split)
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        lines = output.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], names)
        self.assertEqual(lines[1], '')

        (code, output, errs) = run_parser(['-f', 'yaml', '-r', root,
                                           'related'] + query_split)
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = yaml.load(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)

        (code, output, errs) = run_parser(['-f', 'json', '-r', root,
                                           'related'] + query_split)
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)

    @ddt.data(
        ('test_data/override',
         'eno1',
         'eno1'),
        ('test_data/full-9000',
         'br-enp4s0',
         'enp4s0'),
        ('test_data/full-9002',
         'enp2s0.617 br-enp4s0',
         'enp2s0 enp4s0'),
    )
    @ddt.unpack
    def test_physical(self, root, query, names):
        # type: (TestCmdNetPlanParser, str, str, str) -> None
        """
        Test "netplan-parser physical".
        """
        query_split = query.split(' ')
        (code, output, errs) = run_parser(['-f', 'names', '-r', root,
                                           'physical'] + query_split)
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        lines = output.split('\n')
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], names)
        self.assertEqual(lines[1], '')

        (code, output, errs) = run_parser(['-f', 'yaml', '-r', root,
                                           'physical'] + query_split)
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = yaml.load(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)

        (code, output, errs) = run_parser(['-f', 'json', '-r', root,
                                           'physical'] + query_split)
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(' '.join(sorted(data.keys())), names)

    def test_exclude(self):
        # type: (TestCmdNetPlanParser) -> None
        """
        Test "netplan-parser -x conffile show".
        """
        (code, output, errs) = run_parser(['-f', 'yaml',
                                           '-r', 'test_data/full-9002',
                                           'show', 'enp2s0'])
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = yaml.load(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(list(data.keys()), ['enp2s0'])
        self.assertEqual(data['enp2s0'].get('mtu', 1500), 9002)

        (code, output, errs) = run_parser(['-f', 'yaml',
                                           '-r', 'test_data/full-9002',
                                           '-x', '99-storpool.yaml',
                                           'show', 'enp2s0'])
        self.assertEqual(errs, '')
        self.assertEqual(code, 0)
        data = yaml.load(output)
        self.assertIsInstance(data, dict)
        self.assertEqual(list(data.keys()), ['enp2s0'])
        self.assertEqual(data['enp2s0'].get('mtu', 1500), 9000)
