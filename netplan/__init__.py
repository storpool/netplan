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
A Python library for parsing the netplan configuration data.

This module parses the YAML configuration files describing the system's
network configuration in the format used by the netplan.io package.
The main parser is the netplan.parser.Parser class (also exported as
netplan.Parser); its parse() method returns a data structure of
the netplan.config.NetPlan class (also exported as netplan.NetPlan).

Example usage:

    import netplan

    p = netplan.Parser()
    data = p.parse()
    for iface, cfg in data.items():
        print('{section}/{name}'.format(section=cfg.section, name=iface)

    p = netplan.Parser()
    data = p.parse(exclude=['set-mtu.yaml'])
    fix = {'version': 2}
    for iface, cfg in data.get_all_interfaces(['br-enp4s0']).data.items():
        if cfg.get('mtu') != 9000:
            if cfg.section not in fix:
                fix[cfg.section] = {}
            fix[cfg.section][iface] = {'mtu': 9000}
    fix = {'network': fix}
    with open('/etc/netplan/set-mtu.yaml', mode='w') as f:
        print(yaml.dump(fix), file=f, end='')
"""


from .config import NetPlan
from .parser import Parser

VERSION = NetPlan.VERSION

assert len(Parser.NETPLAN_DIRS) == 3
assert [d for d in Parser.NETPLAN_DIRS if not d.endswith("/netplan")] == []
