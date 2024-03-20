# Antares Study Version

[![PyPI - Version](https://img.shields.io/pypi/v/antares-study-version.svg)](https://pypi.org/project/antares-study-version)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/antares-study-version.svg)](https://pypi.org/project/antares-study-version)

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [StudyVersion](#studyversion)
  - [SolverVersion](#solverversion)
  - [Pydantic model](#pydantic-model)
- [Development](#development)
- [License](#license)

## Overview

The `antares-study-version` package defines `StudyVersion` and `SolverVersion` classes to manage version numbers.
It can be used to manage the version of a study, but also the version
of [Antares Solver](https://github.com/AntaresSimulatorTeam/Antares_Simulator).
It supports the [semver](https://semver.org/) format ("major.minor.patch") and the integer format
(major*100 + minor*10 + patch), which is specific to Antares.

This module harmonizes the management of versions in Antares:

- at the level of Antares studies (configuration files, database, etc.)
- at the level of Antares applications, in particular [AntaREST](https://github.com/AntaresSimulatorTeam/AntaREST/).

In the data of a study and in the programs, we encounter several version formats:

- dotted string (ex. "8.7" or "8.7.2"),
- compact string (ex. `"870"`),
- integer (ex. `870`).
- tuples or lists (ex. `(8, 7)` or `[8, 7, 2]`).
- dictionaries (ex. `{"major": 8, "minor": 7, "patch": 2}`).

For instance, since
[version 9.0](https://antares-simulator.readthedocs.io/en/latest/reference-guide/13-file-format/#v900)
of Antares Solver, versions are stored as dotted strings;
the compact format is now obsolete (backward compatibility is ensured for versions prior to 9.0);

For instance, the `study.antares` configuration file now uses the "X.Y" format for the study version instead of the "
XYZ" format.

```ini
[antares]
version = 9.1
caption = My Study
created = 1618413128
lastsave = 1625583204
author = John DOE
```

This module allows to convert these formats to each other, and to compare versions.

## Installation

```console
pip install antares-study-version
```

## Usage

This package provides a `StudyVersion` class to manage study version numbers,
and a `SolverVersion` class to manage Antares Solver version numbers.

The difference between `StudyVersion` and `SolverVersion` is that Solver versions are generally on 3 digits
(with the `major`, `minor` and `patch` components), while study versions are on 2 digits
(with the `major` and `minor` components only), and the `patch` component is not used (always 0).

### StudyVersion

Using the `antares-study-version` module is straightforward:

```python
from antares.study.version import StudyVersion

version = StudyVersion(8, 7, 2)  # patch component is not used
print(version)  # 8.7
```

You can also create a version object from a dotted string:

```python
from antares.study.version import StudyVersion

version = StudyVersion.parse("8.7")
print(version)  # 8.7
```

You can create a version object from a compact string:

```python
from antares.study.version import StudyVersion

version = StudyVersion.parse("870")
print(version)  # 8.7
```

You can create a version object from an integer:

```python
from antares.study.version import StudyVersion

version = StudyVersion.parse(870)
print(version)  # 8.7
```

You can compare versions:

```python
from antares.study.version import StudyVersion

version1 = StudyVersion(8, 6)
version2 = StudyVersion(8, 7)
print(version1 < version2)  # True
```

You can convert a version to string using format specifiers:

```python
from antares.study.version import StudyVersion

version = StudyVersion(8, 7)
print(f"{version}")  # 8.7
print(f"{version:02d}")  # 08.07
print(f"{version:03d}")  # 08.07.00
print(f"{version:ddd}")  # 870
```

You can convert a version to an integer:

```python
from antares.study.version import StudyVersion

version = StudyVersion(8, 7)
print(int(version))  # 870
```

### SolverVersion

Of course, the same operations can be done with `SolverVersion` objects, but with 3 digits:

```python
from antares.study.version import SolverVersion

version = SolverVersion(8, 7, 2)
print(version)  # 8.7.2
```

Objects of the `StudyVersion` and `SolverVersion` classes can be compared to each other:

```python
from antares.study.version import StudyVersion, SolverVersion

study_version = StudyVersion(8, 7)
solver_version = SolverVersion(8, 7, 2)
print(study_version <= solver_version)  # True
```

### Pydantic model

You can even use the `StudyVersion` or `SolverVersion` classes in a Pydantic model:

```python
import datetime
import typing as t
import uuid

from pydantic import BaseModel, Field, validator

from antares.study.version import StudyVersion


class StudyDTO(BaseModel):
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4())
    name: str
    version: StudyVersion
    created: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc))

    @validator("version", pre=True)
    def _validate_version(cls, v: t.Any) -> StudyVersion:
        return StudyVersion.parse(v)


study = StudyDTO(name="foo", version=StudyVersion(4, 5))
obj = study.json()
print(obj)
# {
#     "created": "2024-12-31T12:30:00+00:00",
#     "id": "4930a577-63d2-4ea9-b0b9-581110d97475",
#     "name": "foo",
#     "version": {"major": 4, "minor": 5, "patch": 0}
# }
```

## Development

This projet uses [Hach](https://hatch.pypa.io/latest/) to manage the development environment.

### Project setup

➢ To install the [development environment](https://hatch.pypa.io/latest/environment/), run:

```shell
hatch env create
```

> See [hatch env create](https://hatch.pypa.io/latest/cli/reference/#hatch-env-create) documentation

This command will create a virtual environment and install the development dependencies.

> NOTE: `hatch` creates a virtual environment in the `~/.local/share/hatch/env/virtual/antares-study-version` directory.

➢ To activate the virtual environment, run:

```shell
hatch shell
```

> See [hatch shell](https://hatch.pypa.io/latest/cli/reference/#hatch-shell) documentation

This command will spawn a new shell with the virtual environment activated. Use Ctrl+D to exit the shell.

> NOTE: this command will display the full path to the virtual environment.
> You can use it to configure PyCharm or Visual Studio Code to use this virtual environment.

### Development tasks

➢ To format and lint the source code with [ruff](https://docs.astral.sh/ruff/), run:

```shell
hatch fmt
```

> See [hatch fmt](https://hatch.pypa.io/latest/cli/reference/#hatch-fmt) documentation

➢ To run the tests, run:

```shell
hatch run test
```

> See [hatch run](https://hatch.pypa.io/latest/cli/reference/#hatch-run) documentation

➢ To generate the test coverage report, run:

```shell
hatch run cov
```

This command will run the unit tests and generate a coverage report in the `htmlcov` directory.

➢ To check the typing with [mypy](http://mypy-lang.org/), run:

```shell
hatch run types:check
```

➢ To check the typing on unit tests, run:

```shell
hatch run types:check-tests
```

### Building the package

➢ To build the package, run:

```shell
hatch build
```

This command will create a `dist` directory with the built package.

➢ To build the package and upload it to [PyPI](https://pypi.org/), run:

```shell
hatch publish
```

➢ To clean the project, run:

```shell
hatch clean
```

This command will remove the `dist` directory.

## License

`antares-study-version` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
