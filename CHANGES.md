# Change log for netplan

## Version 0.3.3 (2018-08-20)

- in setup.py, obtain the netplan version string using a regex

## Version 0.3.2 (2018-08-20)

- add typing as a runtime dependency on Python 2.x

## Version 0.3.1 (2018-08-20)

- add type hints
- fix some pylint nits
- use `yaml.safe_load()` instead of `yaml.load()`
- add PyYAML as a runtime dependency
- reformat the source code using black
- use pytest instead of ostestr and simplify the unit tests
- use relative imports in `__init__.py`

## Version 0.3.0 (2018-08-01)

- update the package metadata in setup.py

## Version 0.2.0 (2018-07-31)

- add the "-x filename" argument to netplan-parser

## Version 0.1.0 (2018-07-31)

- initial public release
