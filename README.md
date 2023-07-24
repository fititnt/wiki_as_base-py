# wiki_as_base-py
[MVP] Use MediaWiki Wiki page content as read-only database. Python library implementation. See https://github.com/fititnt/openstreetmap-serverless-functions/tree/main/function/wiki-as-base

[![GitHub](https://img.shields.io/badge/GitHub-fititnt%2Fwiki_as_base--py-lightgrey?logo=github&style=social[fititnt/wiki_as_base-py] "GitHub")](https://github.com/fititnt/wiki_as_base-py)
[![Pypi: wiki_as_base](https://img.shields.io/badge/python%20pypi-wiki_as_base-brightgreen[Python] 
 "Pypi: wiki_as_base")](https://pypi.org/project/wiki_as_base)

---
<!-- TOC depthfrom:2 -->

- [Installing](#installing)
    - [Environment variables](#environment-variables)
- [Command line Usage](#command-line-usage)
    - [Quickstart](#quickstart)
    - [Use of permanent IDs for pages, the WikiMedia pageids](#use-of-permanent-ids-for-pages-the-wikimedia-pageids)
    - [Request multiple pages at once, either by pageid or titles](#request-multiple-pages-at-once-either-by-pageid-or-titles)
    - [Advanced filter with jq](#advanced-filter-with-jq)
    - [Save JSON-LD extracted as files](#save-json-ld-extracted-as-files)
- [Library usage](#library-usage)
    - [Basic use](#basic-use)
    - [Cache remote requests locally](#cache-remote-requests-locally)
    - [Safe inferred data as individual files](#safe-inferred-data-as-individual-files)
- [The JSON-LD Specification](#the-json-ld-specification)
- [Disclaimer / Trivia](#disclaimer--trivia)
- [License](#license)

<!-- /TOC -->
---

## Installing

```bash
pip install wiki_as_base --upgrade

## Alternative:
# pip install wiki_as_base==0.5.10
```

### Environment variables
Customize for your needs. They're shared between command line and the library.

```bash
export WIKI_API='https://wiki.openstreetmap.org/w/api.php'
export WIKI_NS='osmwiki'
export CACHE_TTL='82800'  # 82800 seconds = 23 hours
```

**Suggested**. Customize user agent. [Follows the logic of MediaWiki user agent](https://meta.wikimedia.org/wiki/User-Agent_policy). Without `WIKI_AS_BASE_BOT_CONTACT` customization, for recursive and pagination requests already not cached locally will far slower, with a delay 10 seconds. This default may increase in future releases. Does not affect direct requests (likely ones with less than 50 pages).

<!-- export WIKI_AS_BASE_BOTNAME='wiki_as_base-cli-bot/0.5.10' -->

```bash
export WIKI_AS_BASE_BOT_CONTACT='https://github.com/fititnt/wiki_as_base-py; generic@example.org'
```

<!--
# To increase de delay over the 1

export WIKI_AS_BASE_BOT_CUSTOM_DELAY='60'
export WIKI_INFOBOXES='ValueDescription\nKeyDescription'
export WIKI_DATA_LANGS='yaml\nturtle'
-->

## Command line Usage

### Quickstart

These examples will request two wikies, OpenStreetMap (default)
[live page](https://wiki.openstreetmap.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base)
and Wikidata
[live page](https://www.wikidata.org/wiki/User:EmericusPetro/sandbox/Wiki-as-base).

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

### Use of permanent IDs for pages, the WikiMedia pageids

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

### Request multiple pages at once, either by pageid or titles

Each MediaWiki API may have different limits for batch requests,
however even unauthenticated users often have decent limits (e.g. 50 pages).


> Some Wikies may allow very high limits for authenticated accounts (500 pages),
> however the current version does not implement authenticated requests.

```bash
## All the following commands are equivalent for the default WIKI_API

wiki_as_base --input-autodetect '295916|296167'
wiki_as_base --input-autodetect 'User:EmericusPetro/sandbox/Wiki-as-base|User:EmericusPetro/sandbox/Wiki-as-base/data-validation'
wiki_as_base --pageids '295916|296167'
wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base|User:EmericusPetro/sandbox/Wiki-as-base/data-validation'

```

Trivia: **since this library and CLI fetch directly from WikiMedia API,
and parse Wikitext (not raw HTML),
it causes much less server load to request several pages this way than big ones with higher number of template calls 😉.**

### Advanced filter with jq

When working with the JSON-LD output, you can use jq (_"jq is a lightweight and flexible command-line JSON processor."_), see more on https://stedolan.github.io/jq/, to filter the data


```bash
## Filter tables
wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base' | jq '.data[] | select(.["@type"] == "wtxt:Table")'

## Filter Templates
wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base' | jq '.data[] | select(.["@type"] == "wtxt:Template")'
```

### Save JSON-LD extracted as files

Use `--output-zip-file` parameter. One example:

```bash
wiki_as_base --input-autodetect 'Category:References' --output-zip-file ~/Downloads/Category:References.zip

```

## Library usage

<!--
- See [src/wiki_as_base/cli.py](src/wiki_as_base/cli.py)
- See [tests/](tests/)
-->


> **NOTE**: for production usage (if you can't review releases or are not locked into Docker images)
> consider enforce a very specific release


**Production usage**
```txt
# requirements.txt
wiki_as_base==0.5.10
```

**Other cases (or use in your local machine)**

```bash
# Run this via cli for force redownload lastest. Do not use --pre (pre-releases)
pip install wiki_as_base --upgrade
```

```txt
# requirements.txt
wiki_as_base
```

### Basic use

```python
import json
from wiki_as_base import WikitextAsData

wtxt = WikitextAsData().set_pages_autodetect("295916|296167")
wtxt_jsonld = wtxt.output_jsonld()

print(f'Total: {len(wtxt_jsonld["data"])}')

for resource in wtxt_jsonld["data"]:
    if resource["@type"] == "wtxt:Table":
        print("table found!")
        print(resource["wtxt:tableData"])

print("Pretty print full JSON output")

print(json.dumps(wtxt.output_jsonld(), ensure_ascii=False, indent=2))
```

### Cache remote requests locally

> TODO: port the [requests-cache](https://requests-cache.readthedocs.io/) approach (local SQLite cache database) used on https://github.com/fititnt/openstreetmap-serverless-functions/blob/main/function/wiki-as-base/handler.py .

### Safe inferred data as individual files

```python
import sys
import zipfile
from wiki_as_base import WikitextAsData

wtxt = WikitextAsData().set_pages_autodetect("295916|296167")

# Both output_jsonld() and output_zip() call prepare() (which actually
# make the remote request) plus is_success() on demand.
# However the pythonic way woud be try/except
if not wtxt.prepare().is_success():
    print("error")
    print(wtxt.errors)
    sys.exit(1)

wtxt.output_zip("/tmp/wikitext.zip")

# Using Python zipfile.ZipFile, you can process the file with python
zip = zipfile.ZipFile("/tmp/wikitext.zip")

print("Files inside the zip:")
print(zip.namelist())

# @TODO improve this example on future releases
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

## The JSON-LD Specification

> **NOTE**: work in progress.

https://wtxt.etica.ai/

## Disclaimer / Trivia

The wiki_as_base allows _no-as-complete_ data extraction from MediaWiki markup text directly by its API or direct input,
without need to install server extensions.

Check also the [wikimedia/Wikibase](https://github.com/wikimedia/Wikibase), a full server version (which inspired the name).

## License

Public domain
