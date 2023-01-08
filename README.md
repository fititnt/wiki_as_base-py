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
export WIKI_NS='osmwiki'
```

<!--
export WIKI_INFOBOXES='ValueDescription\nKeyDescription'
export WIKI_DATA_LANGS='yaml\nturtle'
-->

### Command line

```bash
wiki_as_base --help

## Use remote storage (defined on WIKI_API)
wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base'

# The output is JSON-LD. Feel free to further filter the data
wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base' | jq .data[1]

## Example of, instead of use WIKI_API, parse Wiki markup directly. Output JSON- LD
cat tests/data/multiple.wiki.txt | wiki_as_base --input-stdin

## Output zip file instead of JSON-LD. --verbose also adds wikiasbase.jsonld to file
cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-file tests/temp/chatbot-por.zip

## Use different Wiki with ad-hoc change of the env WIKI_API and WIKI_NS
WIKI_NS=wikidatawiki \
  WIKI_API=https://www.wikidata.org/w/api.php \
  wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base'
```

<details>
<summary>Click to see more examples for other wikies</summary>

```bash
# For suggestion of RDF namespaces, see https://dumps.wikimedia.org/backup-index.html
WIKI_NS=specieswiki \
  WIKI_API=https://species.wikimedia.org/w/api.php \
  wiki_as_base --titles 'Paubrasilia_echinata'

# @TODO implement support for MediaWiki version used by wikies like this one
WIKI_NS=smwwiki \
  WIKI_API=https://www.semantic-mediawiki.org/w/api.php \
  wiki_as_base --titles 'Help:Using_SPARQL_and_RDF_stores'


```

</details>

<!--
export WIKI_DATA_LANGS="yaml\nturtle\ntext"
wiki_as_base --titles 'User:EmericusPetro/sandbox/Chatbot-por' | jq .data[0]

wiki_as_base --titles 'User:EmericusPetro/sandbox/Chatbot-por' --output-raw

wiki_as_base --titles 'User:EmericusPetro/sandbox/Chatbot-por'

cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --output-raw

cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-file tests/temp/teste2.zip
cat tests/data/chatbot-por.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-stdout > tests/temp/teste2-stdout.zip

hexcurse tests/temp/teste2.zip
hexcurse tests/temp/teste2-stdout.zip

cat tests/data/edge-case.wiki.txt | wiki_as_base --input-stdin
cat tests/data/multiple.wiki.txt | wiki_as_base --input-stdin --verbose --output-zip-file tests/temp/multiple.zip

wiki_as_base --titles 'Node'

# @TODO test https://wiki.openstreetmap.org/wiki/OSM_XML

https://wiki.openstreetmap.org/wiki/Special:ApiSandbox#action=parse&format=json&title=User%3AEmericusPetro%2Fsandbox%2FWiki-as-base
-->

#### Use of permanent IDs for pages

In case the pages are already know upfront (such as automation) then the use of numeric pageid is a better choice.

```bash
# "--pageids '295916'" is equivalent to "--titles 'User:EmericusPetro/sandbox/Wiki-as-base'"
wiki_as_base --pageids '295916'
```

However, if for some reason (such as strictly enforce not just an exact page,
but exact version of one or more pages) and getting the latest version is not fully essential, then you can use `revids`,

```bash
# "--revids '2460131'" is an older version of --pageids '295916' and
# "--titles 'User:EmericusPetro/sandbox/Wiki-as-base'"
wiki_as_base --revids '2460131'
```

#### Advanced filter with jq

When working with the JSON-LD output, you can use jq (_"jq is a lightweight and flexible command-line JSON processor."_), see more on https://stedolan.github.io/jq/, to filter the data


```bash
## Filter tables
wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base' | jq '.data[] | select(.["@type"] == "wtxt:Table")'

## Filter Templates
wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base' | jq '.data[] | select(.["@type"] == "wtxt:Template")'
```


### Library

- See [examples/](examples/)
- See [tests/](tests/)

> **WARNING**: as 2023-12-05 while the command line is less likely to change,
> the internal calls of this library, names of functions,
> etc are granted to not be stable.

You can import as a pip package, however set the exact version in special if it is unnatended deployment (e.g. GitHub actions, etc).

```txt
# requirements.txt
wiki_as_base==0.5.3
```

<!--

> @TODO add links as URN on https://github.com/EticaAI/urn-resolver/tree/main/resolvers

## JSON-LD context
- See also https://w3c.github.io/json-ld-rc/context.jsonld

## JSON Schema
- See https://json-schema.org/specification.html
- See https://github.com/json-api/json-api/blob/gh-pages/schema

## Namespace
> @TODO make URLS for the namespace

# Returns HTML
curl https://www.w3.org/ns/csvw

# Returns turtle
curl -I -H "Accept: text/turtle" https://www.w3.org/ns/csvw

> @TODO maybe generate page with HTML version of the RDF, see
>       - https://github.com/dgarijo/Widoco

> @TODO investigate about the other formats
https://www.iana.org/assignments/media-types/application/vnd.openstreetmap.data+xml
-->

## The Specification

The temporary docs page is at https://fititnt.github.io/wiki_as_base-py/

## Disclaimer / Trivia

The wiki_as_base allows _no-as-complete_ data extraction from MediaWiki markup text directly by its API or direct input,
without need to install server extensions.

Check also the [wikimedia/Wikibase](https://github.com/wikimedia/Wikibase), a full server version (which inspired the name).

## License

Public domain
