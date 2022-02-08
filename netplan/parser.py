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
A parser for the netplan configuration.
"""


import os

from typing import cast, Any, Dict, Iterable, List, Optional

import yaml

from . import config as npconfig
from . import interface as npiface


_TYPING_USED = (Any, Dict, Iterable, List, Optional)


class ParseFileException(Exception):
    """
    An exception raised while parsing a NetPlan config file.
    """

    def __init__(self, fname, inner):
        # type: (ParseFileException, str, Exception) -> None
        """
        Initialize a ParseFileException object with
        the specified filename and inner exception.
        """
        super().__init__()
        self.fname = fname
        self.inner = inner

    def __str__(self):
        # type: (ParseFileException) -> str
        """
        Provide a human-readable error message.
        """
        return f"Could not parse the {self.fname} netplan config file: {self.inner}"

    def __repr__(self):
        # type: (ParseFileException) -> str
        """
        Provide a Python-style representation.
        """
        return f"ParseFileException(fname={repr(self.fname)}, inner={repr(self.inner)})"


class Parser(object):
    """
    Provide functions for parsing the netplan configuration files.
    """

    # The default list of directories to look in.
    NETPLAN_DIRS = ("/lib/netplan", "/etc/netplan", "/run/netplan")

    # The section names for the various interface classes.
    BY_SECTION = {
        "bonds": npiface.BondInterface,
        "bridges": npiface.BridgeInterface,
        "ethernets": npiface.EthernetInterface,
        "vlans": npiface.VLANInterface,
        "wifis": npiface.WirelessInterface,
    }

    BY_ATTR = ["version", "renderer"]

    def __init__(self, dirs=NETPLAN_DIRS):
        # type: (Parser, Iterable[str]) -> None
        """
        Initialize a Parser object, possibly overriding
        the list of directories to look in for netplan config files.
        """
        self.dirs = dirs

    def find_files(self):
        # type: (Parser) -> List[str]
        """
        Return a list of the full pathnames to the files that will be
        parsed for the netplan configuration.
        """
        # Go through the directories in order, find all files with
        # names that end in *.yaml, then let a file in a later
        # directory override one by the same name in an earlier one.
        #
        dirs = [dirname for dirname in self.dirs if os.path.isdir(dirname)]
        files = {}
        for dirname in dirs:
            for fname in os.listdir(dirname):
                if not fname.endswith(".yaml"):
                    continue
                full = os.path.join(dirname, fname)
                if not os.path.isfile(full):
                    continue
                files[fname] = full

        # Now return the full paths sorted by their base name.
        return [files[name] for name in sorted(files.keys())]

    def _combine_dicts(self, cur, new):
        # type: (Parser, Dict[str, Any], Dict[str, Any]) -> None
        """
        Combine the "cur" and "new" dictionaries:
        - if an item is only in "new", add it to "cur"
        - if an item is in both "cur" and "new", examine the item type:
          - if a list, append the new elements to it
          - if a dictionary, recursively combine the two
          - otherwise, override the "cur" item with the "new" one
        """
        for (key, value) in new.items():
            if key not in cur:
                cur[key] = value
            elif isinstance(value, list):
                cur[key].extend(value)
            elif isinstance(value, dict):
                self._combine_dicts(cur[key], value)
            else:
                cur[key] = value

    def _combine_files(self, files):
        # type: (Parser, List[str]) -> Dict[str, npiface.Interface]
        """
        Read the netplan definitions from the specified files and, for
        each interface in them, create an object of the NetPlan*Interface
        type corresponding to the netplan section that the interface was
        defined in.
        """

        def parse_file(fname):
            # type: (str) -> Dict[str, Any]
            """
            Parse a version 2 netplan file and return a dictionary
            containing the data about the interfaces.
            """
            with open(fname, mode="r", encoding="utf-8") as infile:
                contents = yaml.safe_load(infile)
            if not isinstance(contents, dict):
                raise Exception("The contents is not a YAML dictionary")
            net = contents.get("network")
            if net is None:
                raise Exception('No "network" top-level element')
            ver = net.get("version")
            if ver is None:
                raise Exception('No "network/version" element')
            if ver != 2:
                raise Exception(f"Unsupported format version {ver}")
            missing = sorted(set(net.keys()) - skeys.union(self.BY_ATTR))
            if missing:
                raise Exception(f'Unsupported section(s) {", ".join(missing)}')
            return cast(Dict[str, Any], net)

        raw = {}  # type: Dict[str, Any]
        skeys = set(self.BY_SECTION.keys())
        for fname in files:
            try:
                self._combine_dicts(raw, parse_file(fname))
            except Exception as exc:
                raise ParseFileException(fname=fname, inner=exc) from exc

        data = {}
        for section, ifaces in raw.items():
            if section in self.BY_ATTR:
                data[section] = ifaces
                continue
            cls = self.BY_SECTION[section]
            for iface, idef in ifaces.items():
                data[iface] = cls(iface, section, idef)
        return data

    def parse(self, exclude=None):
        # type: (Parser, Optional[List[str]]) -> npconfig.NetPlan
        """
        Parse the netplan configuration files in the specified
        directories, possibly excluding certain files by name, and
        return a NetPlan object containing the parsed definitions.
        The "exclude" parameter is a list of the filenames (not full
        paths) of the files to be excluded, e.g. ["99-storpool.yaml"].
        """
        files = self.find_files()
        if exclude is not None:
            exs = set(exclude)
            files = [f for f in files if os.path.basename(f) not in exs]
        return npconfig.NetPlan(self._combine_files(files))
