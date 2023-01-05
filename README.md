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
```

<!--
export WIKI_INFOBOXES='ValueDescription\nKeyDescription'
export WIKI_DATA_LANGS='yaml\nturtle'
-->

### Command line

```bash
wiki_as_base --help

## Use remote storage (defined on WIKI_API)
wiki_as_base --page-title 'User:EmericusPetro/sandbox/Wiki-as-base'

# The output is JSON-LD. Feel free to further filter the data
wiki_as_base --page-title 'User:EmericusPetro/sandbox/Wiki-as-base' | jq .data[0]

## Example of, instead of use WIKI_API, parse Wiki markup directly. Output JSON- LD
cat tests/data/multiple.wiki.txt | wiki_as_base --input-stdin


## Output zip file instead of JSON-LD. --verbose also adds wikiasbase.jsonld to file
cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-file tests/temp/chatbot-por.zip
```

<!--
export WIKI_DATA_LANGS="yaml\nturtle\ntext"
wiki_as_base --page-title 'User:EmericusPetro/sandbox/Chatbot-por' | jq .data[0]

wiki_as_base --page-title 'User:EmericusPetro/sandbox/Chatbot-por' --output-raw

wiki_as_base --page-title 'User:EmericusPetro/sandbox/Chatbot-por'

cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --output-raw

cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-file tests/temp/teste2.zip
cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-stdout > tests/temp/teste2-stdout.zip

hexcurse tests/temp/teste2.zip
hexcurse tests/temp/teste2-stdout.zip

cat tests/data/edge-case.wiki.txt | wiki_as_base --input-stdin
cat tests/data/multiple.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-file tests/temp/multiple.zip

wiki_as_base --page-title 'Node'

# @TODO test https://wiki.openstreetmap.org/wiki/OSM_XML

https://wiki.openstreetmap.org/wiki/Special:ApiSandbox#action=parse&format=json&title=User%3AEmericusPetro%2Fsandbox%2FWiki-as-base
-->

### Library

- See [examples/](examples/)
- See [tests/](tests/)

> **WARNING**: as 2023-12-05 while the command line is less likely to change,
> the internal calls of this library, names of functions,
> etc are granted to not be stable.

You can import as a pip package, however set the exact version in special if it is unnatended deployment (e.g. GitHub actions, etc).

```txt
# requirements.txt
wiki_as_base==0.5.2
```

<!--

> @TODO add links as URN on https://github.com/EticaAI/urn-resolver/tree/main/resolvers

## JSON-LD context
- See also https://w3c.github.io/json-ld-rc/context.jsonld

## JSON Schema
- See https://json-schema.org/specification.html
- See https://github.com/json-api/json-api/blob/gh-pages/schema

-->

## The Specification

The temporary docs page is at https://fititnt.github.io/wiki_as_base-py/

## Disclaimer / Trivia

The wiki_as_base allows _no-as-complete_ data extraction from MediaWiki markup text directly by its API or direct input,
without need to install server extensions.

Check also the [wikimedia/Wikibase](https://github.com/wikimedia/Wikibase), a full server version (which inspired the name).

## License

Public domain
