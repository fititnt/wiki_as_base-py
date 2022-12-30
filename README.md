# wiki_as_base-py
[MVP] Use MediaWiki Wiki page content as read-only database. Python library implementation. See https://github.com/fititnt/openstreetmap-serverless-functions/tree/main/function/wiki-as-base

[![GitHub](https://img.shields.io/badge/GitHub-fititnt%2Fwiki_as_base--py-lightgrey?logo=github&style=social[fititnt/wiki_as_base-py] "GitHub")](https://github.com/fititnt/wiki_as_base-py)
[![Pypi: wiki_as_base](https://img.shields.io/badge/python%20pypi-wiki_as_base-brightgreen[Python] 
 "Pypi: wiki_as_base")](https://pypi.org/project/wiki_as_base)

## Installing

```bash
pip install wiki_as_base --upgrade
```

## Usage

### Environment variables
Customize for your needs. They're shared between command line and the library.

```bash
export WIKI_API='https://wiki.openstreetmap.org/w/api.php'
export WIKI_INFOBOXES='ValueDescription\nKeyDescription'
export WIKI_DATA_LANGS='yaml\nturtle'
```

### Command line

```bash
wiki_as_base --help

# Select base page from the Wiki mentioned on WIKI_API
wiki_as_base --page-title 'User:EmericusPetro/sandbox/Wiki-as-base'

# The output is JSON-LD. Feel free to further filter the data
wiki_as_base --page-title 'User:EmericusPetro/sandbox/Wiki-as-base' | jq .data[0]
```

### Library

- See [examples/](examples/)
- See [tests/](tests/)

## Disclaimer / Trivia

The wiki_as_base allows _no-as-complete_ data extraction from MediaWiki markup text directly by its API or direct input,
without need to install server extensions.

Check also the [wikimedia/Wikibase](https://github.com/wikimedia/Wikibase), a full server version (which inspired the name).

## License

Public domain
