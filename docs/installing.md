# Installing

thumbor is distributed as a Python package and can be installed with any
standards-compliant Python package installer.

```{warning}
Current thumbor releases require Python 3.10 or newer. Please refer to
[release notes](https://github.com/thumbor/thumbor/releases)
for details on how to upgrade.
```

## Stable

The latest stable version of thumbor is published on the
[Python Package Index](https://pypi.org/project/thumbor/). Install it with:

```bash
python -m pip install thumbor
```

## From the source of a stable release

Download the latest stable source-code version here on GitHub or PyPI and
decompress it.

From the directory containing the extracted source, run:

```bash
python -m pip install .
```

## From the latest version of the source

Install the latest source directly from GitHub:

```bash
python -m pip install "git+https://github.com/thumbor/thumbor.git"
```

Alternatively, clone the repository and install it locally:

```bash
git clone https://github.com/thumbor/thumbor.git
cd thumbor
python -m pip install .
```

Contributors should use `make setup` instead; it creates the locked uv
development environment with the project's test and optional dependencies.
