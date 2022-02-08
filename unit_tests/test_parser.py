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
Unit tests for the netplan.parser module.
"""

import unittest

from typing import cast, Any, Dict, List, Optional, Set, Type

import ddt

from netplan import interface as npiface
from netplan import parser as npparser


_TYPING_USED = (cast, Any, Dict, List, Optional, Set, Type)


@ddt.ddt
class TestParserCombine(unittest.TestCase):
    # pylint: disable=no-self-use
    """
    Unit tests for the _combine_dict() method.
    """

    @ddt.data(
        ({}, {}, {}),
        ({}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"a": 1, "b": "c"}, {"a": 2}, {"a": 2, "b": "c"}),
        ({"a": [1]}, {}, {"a": [1]}),
        ({"a": [1]}, {"a": [2]}, {"a": [1, 2]}),
        ({"a": {"b": ["c"]}}, {"a": {"b": [0], "e": 17}}, {"a": {"b": ["c", 0], "e": 17}}),
        (
            {"a": 1, "b": {"c": [2], "d": "3"}},
            {"a": 42, "b": {"c": [4], "e": 5}, "f": 6.0},
            {"a": 42, "b": {"c": [2, 4], "d": "3", "e": 5}, "f": 6.0},
        ),
    )
    @ddt.unpack
    def test_combine(
        self,  # type: TestParserCombine
        cur,  # type: Dict[str, Any]
        new,  # type: Dict[str, Any]
        res,  # type: Dict[str, Any]
    ):  # type: (...) -> None
        """
        Unit tests for the _combine_dict() method.
        """
        parser = npparser.Parser()
        data = cur
        parser._combine_dicts(data, new)  # pylint: disable=protected-access
        assert data == res


@ddt.ddt
class TestParser(unittest.TestCase):
    # pylint: disable=no-self-use
    """
    Unit tests for the Parser class.
    """

    def test_by_section(self):
        # type: (TestParser) -> None
        """
        All the values in the npparser.Parser.BY_SECTION dictionary
        should be "real" NetPlan*Interface classes.
        """
        seen = set()  # type: Set[Type[npiface.Interface]]
        for cls in npparser.Parser.BY_SECTION.values():
            assert cls is not npiface.Interface
            assert cls is not npiface.PhysicalInterface
            assert issubclass(cls, npiface.Interface)

            assert cast(Type[npiface.Interface], cls) not in seen
            seen.add(cls)

    def test_override(self):
        # type: (TestParser) -> None
        """
        A file should override a file with the same name in an earlier
        directory.
        """
        parser = npparser.Parser(
            dirs=[
                "test_data/override/lib/netplan",
                "test_data/override/etc/netplan",
                "test_data/override/run/netplan",
            ]
        )
        files = parser.find_files()
        assert files == ["test_data/override/lib/netplan/01-override.yaml"]
        data = parser.parse()
        assert list(data.data.keys()) == ["eno1"]

        parser = npparser.Parser(
            dirs=[
                "test_data/override/lib/netplan",
                "test_data/override/etc-2/netplan",
                "test_data/override/run/netplan",
            ]
        )
        files = parser.find_files()
        assert files == ["test_data/override/etc-2/netplan/01-override.yaml"]
        data = parser.parse()
        assert list(data.data.keys()) == ["eno2"]

    @ddt.data(
        ["01-override.yaml"],
        ["01-override.yaml", "something-else.yaml"],
        ["something-else.yaml", "01-override.yaml"],
    )
    def test_exclude(self, exclude):
        # type: (TestParser, List[str]) -> None
        """
        NetPlanParser.parse() should honor the "exclude" parameter.
        """
        parser = npparser.Parser(
            dirs=[
                "test_data/override/lib/netplan",
                "test_data/override/etc/netplan",
                "test_data/override/run/netplan",
            ]
        )
        files = parser.find_files()
        assert files == ["test_data/override/lib/netplan/01-override.yaml"]
        data = parser.parse(exclude=exclude)
        assert data.data == {}

        parser = npparser.Parser(
            dirs=[
                "test_data/override/lib/netplan",
                "test_data/override/etc-2/netplan",
                "test_data/override/run/netplan",
            ]
        )
        files = parser.find_files()
        assert files == ["test_data/override/etc-2/netplan/01-override.yaml"]
        data = parser.parse(exclude=exclude)
        assert data.data == {}

    @ddt.data(
        ("override", None, "eno1", 1500),
        ("override", [], "eno1", 1500),
        ("full-9000", None, "eno1", 1500),
        ("full-9000", [], "eno1", 1500),
        ("full-9000", ["99-storpool.yaml"], "eno1", 1500),
        ("full-9000", None, "enp2s0.617", 9000),
        ("full-9000", [], "enp2s0.617", 9000),
        ("full-9000", ["99-storpool.yaml"], "enp2s0.617", None),
        ("full-9002", None, "eno1", 1500),
        ("full-9002", [], "eno1", 1500),
        ("full-9002", ["99-storpool.yaml"], "eno1", 1500),
        ("full-9002", None, "enp2s0.617", 9002),
        ("full-9002", [], "enp2s0.617", 9002),
        ("full-9002", ["99-storpool.yaml"], "enp2s0.617", None),
    )
    @ddt.unpack
    def test_mtu(
        self,  # type: TestParser
        subdir,  # type: str
        exclude,  # type: Optional[List[str]]
        iface,  # type: str
        mtu,  # type: Optional[int]
    ):  # type: (...) -> None
        """
        _combine_dict() and "exclude" should work together to
        parse some real-life data files.
        """
        dirs = [f"test_data/{subdir}/{d}/netplan" for d in ("lib", "etc", "run")]
        parser = npparser.Parser(dirs=dirs)
        if exclude is None:
            data = parser.parse()
        else:
            data = parser.parse(exclude=exclude)
        assert iface in data.data
        assert data.data[iface].get("mtu") == mtu

    @ddt.data(
        ("override", ["eno1"], "ethernets: eno1", "ethernets: eno1"),
        ("full-9000", ["eno1"], "ethernets: eno1", "ethernets: eno1"),
        ("full-9000", ["enp2s0.617"], "ethernets: enp2s0; vlans: enp2s0.617", "ethernets: enp2s0"),
        ("full-9000", ["br-enp4s0"], "bridges: br-enp4s0; ethernets: enp4s0", "ethernets: enp4s0"),
        (
            "full-9000",
            ["br-enp4s0", "enp2s0.617"],
            "bridges: br-enp4s0; ethernets: enp2s0, enp4s0; vlans: enp2s0.617",
            "ethernets: enp2s0, enp4s0",
        ),
    )
    @ddt.unpack
    def test_related(
        self,  # type: TestParser
        subdir,  # type: str
        ifaces,  # type: List[str]
        parents,  # type: str
        phys,  # type: str
    ):  # type: (...) -> None
        """
        get_all_interfaces() should return all the related interfaces, and
        get_physical_interfaces() should only return physical interfaces.
        """
        dirs = [f"test_data/{subdir}/{d}/netplan" for d in ("lib", "etc", "run")]
        parser = npparser.Parser(dirs=dirs)
        data = parser.parse()
        assert set(ifaces).issubset(set(data.data.keys()))
        assert str(data.get_all_interfaces(ifaces)) == parents
        assert str(data.get_physical_interfaces(ifaces)) == phys
