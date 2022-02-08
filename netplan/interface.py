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
Data structures describing the netplan interface definitions.
"""


from typing import cast, Any, Dict, List, Optional


_TYPING_USED = (Any, Dict, List, Optional)


class Interface(object):
    """
    A parent class for the netplan interface definitions.
    """

    # TODO: add the schema and validate using it.
    def __init__(self, name, section, data):
        # type: (Interface, str, str, Dict[str, Any]) -> None
        self.name = name
        self.section = section
        self.data = data

    def __str__(self):
        # type: (Interface) -> str
        return f"{self.section}/{self.name}"

    def __repr__(self):
        # type: (Interface) -> str
        return "{cls}(name={name}, section={sect}, data={data})".format(  # pylint: disable=C0209
            cls=type(self).__name__,
            name=repr(self.name),
            sect=repr(self.section),
            data=repr(self.data),
        )

    def get(self, name, default=None):
        # type: (Interface, str, Optional[Any]) -> Any
        """
        Get an interface's property.
        """
        return self.data.get(name, default)

    def set(self, name, value):
        # type: (Interface, str, Any) -> None
        """
        Set an interface's property.
        """
        self.data[name] = value

    def get_parent_names(self):  # pylint: disable=R0201
        # type: (Interface) -> List[str]
        """
        Return the names of any parent interfaces that should be
        examined in addition to this one.
        """
        raise Exception(f"{type(self).__name__}.get_parent_names() must be overridden")


class PhysicalInterface(Interface):
    """
    A parent class for netplan interface definitions for interfaces with
    an actual physical datalink (e.g. Ethernet or wi-fi ones.
    """


class EthernetInterface(PhysicalInterface):
    """
    A netplan definition for an Ethernet interface.
    """

    # TODO: add the additional schema fields.
    def get_parent_names(self):
        # type: (EthernetInterface) -> List[str]
        """
        Return the names of any parent interfaces that should be
        examined in addition to this one.
        For an Ethernet interface, this is an empty list.
        """
        return []


class WirelessInterface(PhysicalInterface):
    """
    A netplan definition for a wireless interface.
    """

    # TODO: add the additional schema fields.
    def get_parent_names(self):
        # type: (WirelessInterface) -> List[str]
        """
        Return the names of any parent interfaces that should be
        examined in addition to this one.
        For a wireless interface, this is an empty list.
        """
        return []


class BondInterface(Interface):
    """
    A netplan definition for a bond interface.
    """

    # TODO: add the additional schema fields.
    def get_parent_names(self):
        # type: (BondInterface) -> List[str]
        """
        Return the names of any parent interfaces that should be
        examined in addition to this one.
        For a bond interface, this is the list of the members.
        """
        return cast(List[str], self.get("interfaces", []))


class BridgeInterface(Interface):
    """
    A netplan definition for a bridge interface.
    """

    # TODO: add the additional schema fields.
    def get_parent_names(self):
        # type: (BridgeInterface) -> List[str]
        """
        Return the names of any parent interfaces that should be
        examined in addition to this one.
        For a bridge interface, this is the list of the members.
        """
        return cast(List[str], self.get("interfaces", []))


class VLANInterface(Interface):
    """
    A netplan definition for a VLAN interface.
    """

    # TODO: add the additional schema fields.
    def get_parent_names(self):
        # type: (VLANInterface) -> List[str]
        """
        Return the names of any parent interfaces that should be
        examined in addition to this one.
        For a VLAN interface, this is the link-level interface that
        the VLAN is on.
        """
        link = self.get("link")
        return [link] if link is not None else []
