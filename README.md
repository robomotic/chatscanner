# chatscanner

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![PyPI - Status](https://img.shields.io/badge/pypi-unreleased-lightgrey.svg)]()

A Python package and CLI tool to scan websites for chatbots.

## Features
- Command-line interface (CLI) for scanning websites
- Easily extensible for custom chatbot detection logic

## Installation

```bash
pip install .
```

## Usage

### CLI

```bash
chatscanner https://example.com --mode basic --output text
chatscanner https://example.com https://another.com --mode basic --output json
```

This will run the scan in the selected mode and output format.

## Development

- Source code is in `src/chatscanner/`
- Tests should go in the `tests/` directory

## Dependencies
- click>=8.0
- requests
- beautifulsoup4

## License
Apache-2.0
