# netplan - a Python library for parsing the netplan configuration data.

## Description

This module parses the YAML configuration files describing the system's
network configuration in the format used by the netplan.io package.
The main parser is the "netplan.parser.Parser" class (also exported as
"netplan.Parser"); its "parse()" method returns a data structure of
the "netplan.config.NetPlan" class (also exported as "netplan.NetPlan").

## Example usage

    import netplan
    import yaml

    p = netplan.Parser()
    data = p.parse()
    for iface, cfg in data.items():
        print('{section}/{name}'.format(section=cfg.section, name=iface))

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

## The netplan-parser tool

The three types of queries - parse the interface data, get all related
interfaces, and get only the physical related interfaces - are also
available via the command-line `netplan-parser` tool:

    # Show the configuration of all interfaces in YAML format
    netplan-parser show

    # Show the configuration of the specified interfaces in JSON format
    netplan-parser -f json show eno1 eno2.617

    # List the names of the interfaces related to the specified one
    netplan-parser -f names related eno2.617

    # Show the configuration of the physical interfaces related to
    # the specified ones
    netplan-parser --format=json physical eno2.617 br1-eno1

## Contact

The `netplan` Python library was written by Peter Pentchev as part of
the [OpenStack development][openstack-dev] team at [StorPool][storpool].

[openstack-dev]: mailto:openstack-dev@storpool.com
[storpool]: https://storpool.com/
