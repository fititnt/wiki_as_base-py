#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  wiki_as_base.py
#
#         USAGE:  ---
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  ---
#       CREATED:  ---
# ==============================================================================

import os
import re
from typing import List, Union
import requests

_REFVER = "0.3.0"

USER_AGENT = os.getenv("USER_AGENT", "wiki-as-base/" + _REFVER)
WIKI_API = os.getenv("WIKI_API", "https://wiki.openstreetmap.org/w/api.php")

WIKI_INFOBOXES = os.getenv("WIKI_INFOBOXES", "ValueDescription\nKeyDescription")

# @TODO WIKI_INFOBOXES_IDS
WIKI_INFOBOXES_IDS = os.getenv("WIKI_INFOBOXES_IDS", "{key}={value}\n{key}")


# @TODO add other common formats on <syntaxhighlight lang="">
_default_langs = [
    "yaml",
    "turtle",
    "json",
    "cpp",
    "text",
    "sql",
    "sparql",
]

# WIKI_DATA_LANGS = os.getenv("WIKI_DATA_LANGS", "yaml\nturtle\ntext\ncpp\nsparql\nsql")
WIKI_DATA_LANGS = os.getenv("WIKI_DATA_LANGS", "\n".join(_default_langs))
# CACHE_DRIVER = os.getenv("CACHE_DRIVER", "sqlite")
# CACHE_TTL = os.getenv("CACHE_TTL", "3600")  # 1 hour

# # @see https://requests-cache.readthedocs.io/en/stable/
# requests_cache.install_cache(
#     "osmapi_cache",
#     # /tmp OpenFaaS allow /tmp be writtable even in read-only mode
#     # However, is not granted that changes will persist or shared
#     db_path="/tmp/osmwiki_cache.sqlite",
#     backend=CACHE_DRIVER,
#     expire_after=CACHE_TTL,
#     allowable_codes=[200, 400, 404, 500],
# )

# @see https://docs.python.org/pt-br/3/library/re.html#re-objects
# @see https://github.com/earwig/mwparserfromhell
# @see https://github.com/siznax/wptools

# @see https://regex101.com/r/rwCoVw/1
# REG = re.compile('<syntaxhighlight lang=\"([a-z0-9]{2,20})\">(.*?)</syntaxhighlight>', flags='gmus')
REG_SH_GENERIC = re.compile(
    '<syntaxhighlight lang="(?P<lang>[a-z0-9]{2,20})">(?P<data>.*?)</syntaxhighlight>',
    flags=re.M | re.S | re.U,
)


def wiki_as_base_all(
    wikitext: str,
    template_keys: List[str] = None,
    syntaxhighlight_langs: List[str] = None,
) -> dict:
    #   "$schema": "https://urn.etica.ai/urn:resolver:schema:api:base",
    #   "@context": "https://urn.etica.ai/urn:resolver:context:api:base",
    data = {
        # TODO: make a permanent URL
        "@context": "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/context.jsonld",
        "$schema": "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/schema.json",
        # Maybe move @type out here
        "@type": "wiki/wikiasbase",
        # @TODO implement errors
        "data": [],
    }

    # set template_keys = False to ignore WIKI_INFOBOXES
    if template_keys is None and len(WIKI_INFOBOXES) > 0:
        template_keys = WIKI_INFOBOXES.splitlines()

    if template_keys is not None and len(template_keys) > 0:
        for item in template_keys:
            result = wiki_as_base_from_infobox(wikitext, item)
            if result:
                data["data"].append(result)

    # set syntaxhighlight_langs = False to ignore WIKI_DATA_LANGS
    if syntaxhighlight_langs is None and len(WIKI_DATA_LANGS) > 0:
        syntaxhighlight_langs = WIKI_DATA_LANGS.splitlines()

    if syntaxhighlight_langs is not None and len(syntaxhighlight_langs) > 0:
        for item in syntaxhighlight_langs:
            results = wiki_as_base_from_syntaxhighlight(wikitext, item)
            # results = wiki_as_base_from_syntaxhighlight(wikitext)
            if results:
                for result in results:
                    if not result:
                        continue
                    if result[2]:
                        data["data"].append(
                            {
                                "@type": "wiki/data/" + result[1],
                                "@id": result[2],
                                "data_raw": result[0],
                            }
                        )
                    else:
                        data["data"].append(
                            {
                                "@type": "wiki/data/" + result[1],
                                # "@id": result[2],
                                "data_raw": result[0],
                            }
                        )
    return data


def wiki_as_base_from_infobox(
    wikitext: str, template_key: str, id_from: List[str] = None
):
    """wiki_as_base_from_infobox Parse typical Infobox"""
    data = {}
    data["@type"] = "wiki/infobox/" + template_key
    data["@id"] = None
    # data['_allkeys'] = []
    # @TODO https://stackoverflow.com/questions/33862336/how-to-extract-information-from-a-wikipedia-infobox
    # @TODO make this part not with regex, but rules.

    if id_from is None:
        id_from = [
            ("key", "=", "value"),
            ("key"),
        ]

    if wikitext.find("{{" + template_key) == -1:
        return None

    # @TODO better error handling
    if wikitext.count("{{" + template_key) > 1:
        return False

    # if True:
    try:
        start_template = wikitext.split("{{" + template_key)[1]
        raw_lines = start_template.splitlines()
        counter_tag = 1
        index = -1
        for raw_line in raw_lines:
            index += 1
            key = None
            value = None
            if counter_tag == 0:
                break
            raw_line_trimmed = raw_line.strip()
            if raw_line_trimmed.startswith("|"):
                # parts = raw_line_trimmed.split('=')
                if raw_line_trimmed.find("=") > -1:
                    key_tmp, value_tmp = raw_line_trimmed.split("=")
                    key = key_tmp.strip("|").strip()
                else:
                    continue
                    # key = raw_line_trimmed
                # data['_allkeys'].append(key)
                if len(raw_lines) >= index + 1:
                    if raw_lines[index + 1].strip() == "}}" or raw_lines[
                        index + 1
                    ].strip().startswith("|"):
                        # closed
                        data[key] = value_tmp.strip()
                        # pass
                    # pass
                # pass
    except ValueError as error:
        # raise ValueError(error)
        return None

    if id_from is not None and len(id_from):
        for attemps in id_from:
            if len(attemps) == 1 and attemps[0] in data and len(data[attemps[0]]) > 0:
                data["@id"] = data[attemps[0]]
                break
            if len(attemps) == 3 and attemps[0] in data and attemps[2] in data:
                data["@id"] = data[attemps[0]] + attemps[1] + data[attemps[2]]
                break

    if data["@id"] is None:
        del data["@id"]

    return data


def wiki_as_base_from_syntaxhighlight(
    wikitext: str, lang: str = None, has_text: str = None, match_regex: str = None
) -> List[tuple]:
    """wiki_as_base_get_syntaxhighlight _summary_

    _extended_summary_

    Args:
        wikitext (str):            The raw Wiki markup to search for
        lang (str, optional):      The lang on <syntaxhighlight lang="{lang}">.
                                   Defaults to None.
        has_text (str, optional):  Text content is expected to have.
                                   Defaults to None
        match_regex (str, optional): Regex content is expected to match.
                                     Defaults to None

    Returns:
        List[tuple]: List of tuples. Content on first index, lang on second.
                     None if no result found.
    """
    result = []
    if lang is None:
        reg_sh = re.compile(
            '<syntaxhighlight lang="(?P<lang>[a-z0-9]{2,20})">(?P<data>.*?)</syntaxhighlight>',
            flags=re.M | re.S | re.U,
        )
    else:
        reg_sh = re.compile(
            f'<syntaxhighlight lang="(?P<lang>{lang})">(?P<data>.*?)</syntaxhighlight>',
            flags=re.M | re.S | re.U,
        )

    # TODO make comments like <!-- work
    reg_filename = re.compile(
        "[#|\/\/]\s?filename\s?=\s?(?P<filename>[\w\-\_\.]{3,255})", flags=re.U
    )

    items = re.findall(reg_sh, wikitext)

    if len(items) > 0 and has_text is not None:
        original = items
        items = []
        for item in original:
            if item[1].find(has_text) > -1:
                items.append(item)

    if len(items) > 0 and match_regex is not None:
        original = items
        items = []
        for item in original:
            if re.search(match_regex, item[1]) is not None:
                items.append(item)

    if len(items) == 0:
        return None

    # swap order and detect filename
    for item in items:
        data_raw = item[1].strip()

        # We would only check first line for a hint of suggested filename
        items = re.findall(reg_filename, data_raw)
        # print(items, data_raw)
        # raise ValueError(items)
        if items and items[0]:
            result.append((data_raw, item[0], items[0]))
        else:
            result.append((data_raw, item[0], None))

    return result


def wiki_as_base_meta(wikitext: str) -> dict:
    return {}


def wiki_as_base_request(
    title: str,
    # template_key: str,
):
    # Inspired on https://github.com/earwig/mwparserfromhell example
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "rvlimit": 1,
        "titles": title,
        "format": "json",
        "formatversion": "2",
    }

    try:
        headers = {"User-Agent": USER_AGENT}
        req = requests.get(WIKI_API, headers=headers, params=params)
        res = req.json()
        revision = res["query"]["pages"][0]["revisions"][0]
        text = revision["slots"]["main"]["content"]
    except ValueError:
        return None

    return text


def wiki_as_base_raw(wikitext: str) -> dict:
    return wikitext
