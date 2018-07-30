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
Unit tests for the netplan.parser module.
"""

import unittest

import ddt

from netplan import interface as npiface
from netplan import parser as npparser


@ddt.ddt
class TestParserCombine(unittest.TestCase):
    """
    Unit tests for the _combine_dict() method.
    """
    @ddt.data(
        ({},
         {},
         {}),
        ({},
         {'a': 1},
         {'a': 1}),
        ({'a': 1},
         {'a': 2},
         {'a': 2}),
        ({'a': 1, 'b': 'c'},
         {'a': 2},
         {'a': 2, 'b': 'c'}),
        ({'a': [1]},
         {},
         {'a': [1]}),
        ({'a': [1]},
         {'a': [2]},
         {'a': [1, 2]}),
        ({'a': {'b': ['c']}},
         {'a': {'b': [0], 'e': 17}},
         {'a': {'b': ['c', 0], 'e': 17}}),
        ({'a': 1, 'b': {'c': [2], 'd': '3'}},
         {'a': 42, 'b': {'c': [4], 'e': 5}, 'f': 6.0},
         {'a': 42, 'b': {'c': [2, 4], 'd': '3', 'e': 5}, 'f': 6.0}),
    )
    @ddt.unpack
    def test_combine(self, cur, new, res):
        """
        Unit tests for the _combine_dict() method.
        """
        parser = npparser.Parser()
        data = cur
        parser._combine_dicts(data, new)
        self.assertEqual(data, res)


@ddt.ddt
class TestParser(unittest.TestCase):
    """
    Unit tests for the Parser class.
    """
    def test_by_section(self):
        """
        All the values in the npparser.Parser.BY_SECTION dictionary
        should be "real" NetPlan*Interface classes.
        """
        seen = set()
        for cls in npparser.Parser.BY_SECTION.values():
            self.assertIsNot(cls, npiface.Interface)
            self.assertIsNot(cls, npiface.PhysicalInterface)
            self.assertTrue(issubclass(cls, npiface.Interface))

            self.assertNotIn(cls, seen)
            seen.add(cls)

    def test_override(self):
        """
        A file should override a file with the same name in an earlier
        directory.
        """
        parser = npparser.Parser(dirs=[
            'test_data/override/lib/netplan',
            'test_data/override/etc/netplan',
            'test_data/override/run/netplan',
        ])
        files = parser.find_files()
        self.assertEqual(files, [
            'test_data/override/lib/netplan/01-override.yaml',
        ])
        data = parser.parse()
        self.assertEqual(list(data.data.keys()), ['eno1'])

        parser = npparser.Parser(dirs=[
            'test_data/override/lib/netplan',
            'test_data/override/etc-2/netplan',
            'test_data/override/run/netplan',
        ])
        files = parser.find_files()
        self.assertEqual(files, [
            'test_data/override/etc-2/netplan/01-override.yaml',
        ])
        data = parser.parse()
        self.assertEqual(list(data.data.keys()), ['eno2'])

    @ddt.data(
        ['01-override.yaml'],
        ['01-override.yaml', 'something-else.yaml'],
        ['something-else.yaml', '01-override.yaml'],
    )
    def test_exclude(self, exclude):
        """
        NetPlanParser.parse() should honor the "exclude" parameter.
        """
        parser = npparser.Parser(dirs=[
            'test_data/override/lib/netplan',
            'test_data/override/etc/netplan',
            'test_data/override/run/netplan',
        ])
        files = parser.find_files()
        self.assertEqual(files, [
            'test_data/override/lib/netplan/01-override.yaml',
        ])
        data = parser.parse(exclude=exclude)
        self.assertEqual(data.data, {})

        parser = npparser.Parser(dirs=[
            'test_data/override/lib/netplan',
            'test_data/override/etc-2/netplan',
            'test_data/override/run/netplan',
        ])
        files = parser.find_files()
        self.assertEqual(files, [
            'test_data/override/etc-2/netplan/01-override.yaml',
        ])
        data = parser.parse(exclude=exclude)
        self.assertEqual(data.data, {})

    @ddt.data(
        ('override', None, 'eno1', 1500),
        ('override', [], 'eno1', 1500),

        ('full-9000', None, 'eno1', 1500),
        ('full-9000', [], 'eno1', 1500),
        ('full-9000', ['99-storpool.yaml'], 'eno1', 1500),
        ('full-9000', None, 'enp2s0.617', 9000),
        ('full-9000', [], 'enp2s0.617', 9000),
        ('full-9000', ['99-storpool.yaml'], 'enp2s0.617', None),

        ('full-9002', None, 'eno1', 1500),
        ('full-9002', [], 'eno1', 1500),
        ('full-9002', ['99-storpool.yaml'], 'eno1', 1500),
        ('full-9002', None, 'enp2s0.617', 9002),
        ('full-9002', [], 'enp2s0.617', 9002),
        ('full-9002', ['99-storpool.yaml'], 'enp2s0.617', None),
    )
    @ddt.unpack
    def test_mtu(self, subdir, exclude, iface, mtu):
        """
        _combine_dict() and "exclude" should work together to
        parse some real-life data files.
        """
        dirs = ['test_data/{sub}/{d}/netplan'.format(sub=subdir, d=d)
                for d in ('lib', 'etc', 'run')]
        parser = npparser.Parser(dirs=dirs)
        if exclude is None:
            data = parser.parse()
        else:
            data = parser.parse(exclude=exclude)
        self.assertIn(iface, data.data)
        self.assertEqual(data.data[iface].get('mtu'), mtu)

    @ddt.data(
        ('override',
         ['eno1'],
         'ethernets: eno1',
         'ethernets: eno1'),
        ('full-9000',
         ['eno1'],
         'ethernets: eno1',
         'ethernets: eno1'),
        ('full-9000',
         ['enp2s0.617'],
         'ethernets: enp2s0; vlans: enp2s0.617',
         'ethernets: enp2s0'),
        ('full-9000',
         ['br-enp4s0'],
         'bridges: br-enp4s0; ethernets: enp4s0',
         'ethernets: enp4s0'),
        ('full-9000',
         ['br-enp4s0', 'enp2s0.617'],
         'bridges: br-enp4s0; ethernets: enp2s0, enp4s0; vlans: enp2s0.617',
         'ethernets: enp2s0, enp4s0'),
    )
    @ddt.unpack
    def test_related(self, subdir, ifaces, parents, phys):
        """
        get_all_interfaces() should return all the related interfaces, and
        get_physical_interfaces() should only return physical interfaces.
        """
        dirs = ['test_data/{sub}/{d}/netplan'.format(sub=subdir, d=d)
                for d in ('lib', 'etc', 'run')]
        parser = npparser.Parser(dirs=dirs)
        data = parser.parse()
        self.assertTrue(set(ifaces).issubset(set(data.data.keys())))
        self.assertEqual(str(data.get_all_interfaces(ifaces)), parents)
        self.assertEqual(str(data.get_physical_interfaces(ifaces)), phys)
