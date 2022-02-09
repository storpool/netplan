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
Convenience classes for the fully-parsed netplan configuration.
"""

from typing import Dict, List, Set, Any

from . import interface as npiface


_TYPING_USED = (Dict, List, Set)


class NetPlan(object):
    """
    A full netplan configuration; the "data" member is a dictionary of
    interface names to netplan.interface.* classes.
    """

    VERSION = "0.4.1"

    def __init__(self, data):
        # type: (NetPlan, Dict[str, Any]) -> None
        self.version: int = 0
        if "version" in data.keys():
            self.version = data["version"]
            del data["version"]
        self.renderer: str = ""
        if "renderer" in data.keys():
            self.renderer = data["renderer"]
            del data["renderer"]
        self.data: Dict[str, npiface.Interface] = data

    def __str__(self):
        # type: (NetPlan) -> str
        """
        Provide a human-readable list of the interfaces grouped by section.
        """
        # Group the interfaces by section
        by_section = {}  # type: Dict[str, List[str]]
        for iface, cfg in self.data.items():
            if cfg.section not in by_section:
                by_section[cfg.section] = []
            by_section[cfg.section].append(iface)

        # Sort the interface names within each section
        collected = [
            f'{section}: {", ".join(sorted(data))}' for (section, data) in by_section.items()
        ]

        # Return a list sorted by section name
        return "; ".join(sorted(collected))

    def __repr__(self):
        # type: (NetPlan) -> str
        """
        Provide a Python-style representation.
        """
        return f"NetPlan({repr(self.data)})"

    def get_net_version(self):
        # type: (NetPlan) -> Dict[str, int]
        """
        Return the NetPlan YAML version.
        """
        if self.version != 0:
            return {"version": self.version}
        return {}

    def get_net_renderer(self):
        # type: (NetPlan) -> Dict[str, str]
        """
        Return the NetPlan renderer.
        """
        if self.version:
            return {"renderer": self.renderer}
        return {}

    def get_all_interfaces(self, ifaces):
        # type: (NetPlan, List[str]) -> NetPlan
        """
        Get the configuration of the interfaces with the specified names and
        all their parents recursively.
        """
        cur = set()  # type: Set[str]
        new = set(ifaces)
        while new:
            cur = cur.union(new)
            newnew = set()  # type: Set[str]
            for iface in new:
                newnew = newnew.union(set(self.data[iface].get_parent_names()) - cur)
            new = newnew
        return NetPlan({iface: self.data[iface] for iface in cur})

    def get_physical_interfaces(self, ifaces):
        # type: (NetPlan, List[str]) -> NetPlan
        """
        Similar to get_all_interfaces(), but only return physical interfaces.
        For instance, for a VLAN interface over a bridge over two VLANs
        over Ethernet interfaces this function would only return
        the definitions for the Ethernet interfaces.  For an Ethernet or
        wireless interface this function would return its own configuration.
        """
        related = self.get_all_interfaces(ifaces)
        phys = [d for d in related.data.values() if isinstance(d, npiface.PhysicalInterface)]
        return NetPlan({d.name: d for d in phys})
