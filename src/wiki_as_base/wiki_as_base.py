#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  wiki_as_base.py
#
#         USAGE:  # this is a library. Import into your code:
#                     from wiki_as_base import *
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#                   - lxml
#          BUGS:  - No big XML dumps output format support (not yet)
#                 - No support for PBF Format (...not yet)
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.3.0
#       CREATED:  2022-11-25 19:22:00Z v0.1.0 started
#      REVISION:  2022-11-26 20:47:00Z v0.2.0 node, way, relation basic turtle,
#                                      only attached tags (no <nd> <member> yet)
#                 2022-12-21 01:46:00Z v0.3.0 osmrdf2022.py -> wiki_as_base.py
# ==============================================================================

import re

# @see https://docs.python.org/pt-br/3/library/re.html#re-objects

# @see https://regex101.com/r/rwCoVw/1
# REG = re.compile('<syntaxhighlight lang=\"([a-z0-9]{2,20})\">(.*?)</syntaxhighlight>', flags='gmus')
REG_SH_GENERIC = re.compile(
    '<syntaxhighlight lang=\"([a-z0-9]{2,20})\">(.*?)</syntaxhighlight>',
    flags=re.M | re.S | re.U)


def wiki_as_base_raw(wikitext: str) -> dict:
    return wikitext


def wiki_as_base_meta(wikitext: str) -> dict:
    return {}


# @see https://stackoverflow.com/questions/6227706/parsing-wikitext-with-regex-in-java
