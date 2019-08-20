#!/usr/bin/env python
#
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

import re
import setuptools


RE_VERSION = r"""^
    \s* VERSION \s* = \s* "
    (?P<version>
           (?: 0 | [1-9][0-9]* )    # major
        \. (?: 0 | [1-9][0-9]* )    # minor
        \. (?: 0 | [1-9][0-9]* )    # patchlevel
    (?: \. [a-zA-Z0-9]+ )?          # optional addendum (dev1, beta3, etc.)
    )
    " \s*
    $"""


def get_version():
    # type: () -> str
    """ Get the version string from the module's __init__ file. """
    found = None
    re_semver = re.compile(RE_VERSION, re.X)
    with open("netplan/config.py") as init:
        for line in init.readlines():
            match = re_semver.match(line)
            if not match:
                continue
            assert found is None
            found = match.group("version")

    assert found is not None
    return found


with open("README.md", mode="r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="netplan",
    version=get_version(),
    packages=("netplan",),
    author="StorPool OpenStack development team",
    author_email="openstack-dev@storpool.com",
    description="A library for parsing the netplan configuration data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords="netplan",
    url="https://github.com/storpool/netplan",
    install_requires=["PyYAML", 'typing;python_version<"3"'],
    package_data={"netplan": ["py.typed"]},
    zip_safe=True,
    scripts=["bin/netplan-parser"],
)
