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
Unit tests for the netplan.interface module.
"""

import unittest

from typing import List, Type

import ddt
import pytest

from netplan import interface as npiface


_TYPING_USED = (List, Type)


@ddt.ddt
class TestInterfaces(unittest.TestCase):
    # pylint: disable=no-self-use
    """
    Test various aspects of the *Interface classes.
    """

    @ddt.data(
        npiface.Interface,
        npiface.PhysicalInterface,
        npiface.EthernetInterface,
        npiface.WirelessInterface,
        npiface.VLANInterface,
        npiface.BondInterface,
        npiface.BridgeInterface,
    )
    def test_interfaces_basic(self, cls):
        # type: (TestInterfaces, Type[npiface.Interface]) -> None
        """
        Test some basic functionality of the interface classes.
        """
        obj = cls("iface", "section", {"mtu": 1500})
        assert isinstance(obj, npiface.Interface)
        assert isinstance(obj, cls)
        assert obj.name == "iface"
        assert obj.section == "section"

        assert str(obj) == "section/iface"
        got = repr(obj)
        exp = (
            "{name}(name='iface', section='section', "  # pylint: disable=C0209
            "data={{'mtu': 1500}})".format(name=cls.__name__)
        )
        assert got == exp

        assert obj.data == {"mtu": 1500}
        assert obj.data.get("mtu") == 1500
        assert obj.data.get("mtux") is None
        assert obj.data.get("mtu", 9000) == 1500
        assert obj.data.get("mtux", 9000) == 9000

        obj.set("mtu", 1600)
        assert obj.data == {"mtu": 1600}
        assert obj.data.get("mtu") == 1600
        assert obj.data.get("mtux") is None
        assert obj.data.get("mtu", 9000) == 1600
        assert obj.data.get("mtux", 9000) == 9000

        obj.set("mtux", 1600)
        assert obj.data == {"mtu": 1600, "mtux": 1600}
        assert obj.data.get("mtu") == 1600
        assert obj.data.get("mtux") == 1600
        assert obj.data.get("mtu", 9000) == 1600
        assert obj.data.get("mtux", 9000) == 1600

        if cls is npiface.Interface or cls is npiface.PhysicalInterface:
            with pytest.raises(Exception):
                obj.get_parent_names()
        else:
            assert obj.get_parent_names() == []

    @ddt.data(
        (npiface.EthernetInterface, []),
        (npiface.WirelessInterface, []),
        (npiface.VLANInterface, ["lnk"]),
        (npiface.BondInterface, ["i1", "i2"]),
        (npiface.BridgeInterface, ["i1", "i2"]),
    )
    @ddt.unpack
    def test_parent_interface(self, cls, parents):
        # type: (TestInterfaces, Type[npiface.Interface], List[str]) -> None
        """
        Test querying an interface for its parent.
        """
        obj = cls("iface", "section", {"interfaces": ["i1", "i2"], "link": "lnk"})
        assert obj.get_parent_names() == parents
