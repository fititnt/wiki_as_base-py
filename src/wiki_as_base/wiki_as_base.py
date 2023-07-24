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

# import copy
from abc import ABC
from ast import Tuple
import csv

# from ctypes import Union
import datetime
import io
import json
import os
import re
import sys
import time

# import sys
# from typing import Any, List, Union
from typing import List
import zipfile
import requests
import requests_cache

from .parser import (
    WikipageContext,
    WikisiteContext,
    WikitextOutputFilter,
    parse_all,
    # parse_sections,
    # parse_tables,
    wtxt_text_corpus,
)

from .constants import WIKI_DATA_LANGS

_REFVER = "0.5.10"


WIKI_AS_BASE_BOTNAME = os.getenv(
    "WIKI_AS_BASE_BOTNAME", "wiki_as_base-cli-bot/" + _REFVER
)
_WIKI_AS_BASE_BOT_CONTACT_DEFAULT = (
    "https://github.com/fititnt/wiki_as_base-py; generic@example.org"
)
WIKI_AS_BASE_BOT_CONTACT = os.getenv(
    "WIKI_AS_BASE_BOT_CONTACT", _WIKI_AS_BASE_BOT_CONTACT_DEFAULT
)
WIKI_AS_BASE_LIB = f"wiki_as_base/{_REFVER}"

_USER_AGENT_MERGED = (
    f"{WIKI_AS_BASE_BOTNAME} ({WIKI_AS_BASE_BOT_CONTACT}) {WIKI_AS_BASE_LIB}"
)
USER_AGENT = os.getenv("USER_AGENT", _USER_AGENT_MERGED)
WIKI_API = os.getenv("WIKI_API", "https://wiki.openstreetmap.org/w/api.php")

# Consider using prefix like https://dumps.wikimedia.org/backup-index.html
WIKI_NS = os.getenv("WIKI_NS", "osmwiki")
WIKI_BASE = os.getenv("WIKI_BASE", lambda x: WIKI_API.replace("/w/api.php", "/wiki/"))

# @TODO document better this part
WTXT_PAGE_LIMIT = int(os.getenv("WTXT_PAGE_LIMIT", "50"))
WTXT_PAGE_OFFSET = int(os.getenv("WTXT_PAGE_OFFSET", "0"))

CACHE_DRIVER = os.getenv("CACHE_DRIVER", "sqlite")

# CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
CACHE_TTL = int(os.getenv("CACHE_TTL", "82800"))  # 23 hours

DELAY_GENERIC_CONTACT = int(os.getenv("DELAY_GENERIC_CONTACT", "10"))  # 10 seconds
# DELAY_NONGENERIC_CONTACT = int(
#     os.getenv("DELAY_GENERIC_CONTACT", "0")
# )  # 0 seconds (0 seconds + server delay for pagination)
DELAY_NONGENERIC_CONTACT = 1  # 1 second
WIKI_AS_BASE_BOT_CUSTOM_DELAY = int(
    os.getenv("WIKI_AS_BASE_BOT_CUSTOM_DELAY", DELAY_NONGENERIC_CONTACT)
)

# @see https://requests-cache.readthedocs.io/en/stable/
requests_cache.install_cache(
    "wikiasbase",
    # /tmp OpenFaaS allow /tmp be writtable even in read-only mode
    # However, is not granted that changes will persist or shared
    db_path="/tmp/wikiasbase_cache.sqlite",
    backend=CACHE_DRIVER,
    expire_after=CACHE_TTL,
    allowable_codes=[200, 400, 404, 500],
)

WIKI_INFOBOXES = os.getenv("WIKI_INFOBOXES", "ValueDescription\nKeyDescription")

# @TODO WIKI_INFOBOXES_IDS
WIKI_INFOBOXES_IDS = os.getenv("WIKI_INFOBOXES_IDS", "{key}={value}\n{key}")
_JSONLD_CONTEXT = (
    # "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/context.jsonld"
    "https://wtxt.etica.ai/context.jsonld"
)
_JSONSCHEMA = (
    # "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/schema.json"
    "https://wtxt.etica.ai/schema.json"
)

# @TODO maybe also implement Wikibase fetch?

# https://wiki.openstreetmap.org/wiki/Special:ApiSandbox#action=wbgetentities&format=json&ids=Q12345

# raise ValueError(WIKI_DATA_LANGS)
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
# REG_SH_GENERIC = re.compile(
#     '<syntaxhighlight lang="(?P<lang>[a-z0-9]{2,20})">(?P<data>.*?)</syntaxhighlight>',
#     flags=re.M | re.S | re.U,
# )


def delay_consecutive_request():
    """delay_consecutive_request compute delay for implicit requests

    Returns:
        int: delay in seconds
    """
    # Identified users or not, we allow higher defined delays than the default 10s
    if WIKI_AS_BASE_BOT_CUSTOM_DELAY > DELAY_NONGENERIC_CONTACT:
        return WIKI_AS_BASE_BOT_CUSTOM_DELAY

    if WIKI_AS_BASE_BOT_CONTACT == _WIKI_AS_BASE_BOT_CONTACT_DEFAULT:
        return DELAY_GENERIC_CONTACT
    return DELAY_NONGENERIC_CONTACT


def wiki_as_base_all(
    wikitext: str,
    template_keys: List[str] = None,
    syntaxhighlight_langs: List[str] = None,
    meta: dict = None,
    _next_release: bool = False,
) -> dict:
    """wiki_as_base_all

    @deprecated Use WikitextAsData()
    """

    #   "$schema": "https://urn.etica.ai/urn:resolver:schema:api:base",
    #   "@context": "https://urn.etica.ai/urn:resolver:context:api:base",
    data = {
        # TODO: make a permanent URL
        # "@context": "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/context.jsonld",
        "@context": _JSONLD_CONTEXT,
        # "$schema": "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/schema.json",
        "$schema": _JSONSCHEMA,
        # Maybe move @type out here
        "@type": "wtxt:DataCollection",
        # @TODO implement errors
        "data": None,
        # "meta": {
        #     '_source': None
        # }
    }

    data["data"] = []

    if meta is None:
        meta = {"_source": None}
    if meta is not False:
        data["meta"] = meta

    if _next_release:
        data_raw_key = "data"
    else:
        data_raw_key = "data_raw"

    wth = WikitextHeading(wikitext)
    # outline = wth.get_headings()
    outline = wth.get_outline()
    if outline:
        data["data"].append(
            {
                # "@type": "wiki/outline",
                "@type": "wtxt:DataCollectionOutline",
                "@id": "heading-outline.html",
                # 'data_raw': outline,
                # data_raw_key: outline,
                "wtxt:literalData": outline,
            }
        )

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
                                # "@type": "wiki/data/" + result[1],
                                # "@id": result[2],
                                "@type": "wtxt:PreformattedCode",
                                "wtxt:syntaxLang": result[1],
                                "@id": result[2],
                                "wtxt:literalData": result[0],
                            }
                        )
                    else:
                        data["data"].append(
                            {
                                # "@type": "wiki/data/" + result[1],
                                "@type": "wtxt:PreformattedCode",
                                "wtxt:syntaxLang": result[1],
                                # "@id": result[2],
                                # "data_raw": result[0],
                                # data_raw_key: result[0],
                                "wtxt:literalData": result[0],
                            }
                        )

    wmt = WikitextTable(wikitext)
    tables = wmt.get_tables()
    if tables and len(tables) > 0:
        index = 1
        for table in tables:
            table_data = [table["header"]] + table["data"]

            _tbl = {
                "@type": "wtxt:Table",
                "@id": f"t{index}",
                "wtxt:tableData": table_data,
                "_is_complete": table["_is_complete"],
                "_errors": table["_errors"]
                # "_type": "wtxt:Table",
            }
            # table["@type"] = "wtxt:Table"
            # table["@id"] = f"t{index}"
            # _tbl.update(table)
            data["data"].append(_tbl)
            index += 1

    return data
    # return copy.deepcopy(data)


def wiki_as_base_from_infobox(
    wikitext: str, template_key: str, id_from: List[str] = None
):
    """wiki_as_base_from_infobox Parse typical Infobox

    @see https://en.wikipedia.org/wiki/Help:Infobox

    """
    data = {}
    # data["@type"] = "wiki/infobox/" + template_key
    # data["@id"] = None
    data["@type"] = "wtxt:Template"
    data["@id"] = None
    data["wtxt:templateName"] = template_key
    data["wtxt:templateData"] = {}
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

    _templateData = {}

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
            if raw_line_trimmed == "}}":
                # Abort early to avoid process further down the page
                break
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
                        # data[key] = value_tmp.strip()
                        _templateData[key] = value_tmp.strip()
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

    data["wtxt:templateData"] = _templateData

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
        # example https://wiki.openstreetmap.org/wiki/OSM_XML
        reg_sh_old = re.compile(
            '<source lang="?(?P<lang>[a-z0-9]{2,20})"?>(?P<data>.*?)</source>',
            flags=re.M | re.S | re.U,
        )
    else:
        reg_sh = re.compile(
            f'<syntaxhighlight lang="(?P<lang>{lang})">(?P<data>.*?)</syntaxhighlight>',
            flags=re.M | re.S | re.U,
        )
        reg_sh_old = re.compile(
            f'<source lang="?(?P<lang>{lang})"?>(?P<data>.*?)</source>',
            flags=re.M | re.S | re.U,
        )

    # TODO make comments like <!-- work
    reg_filename = re.compile(
        "[#|\/\/]\s?filename\s?=\s?(?P<filename>[\w\-\_\.]{3,255})", flags=re.U
    )

    items_a = re.findall(reg_sh, wikitext)
    items_b = re.findall(reg_sh_old, wikitext)

    items = [*items_a, *items_b]

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


def wiki_as_base_meta_from_api(wikiapi_meta: dict) -> dict:
    meta = {}
    if "pageid" in wikiapi_meta:
        meta["pageid"] = wikiapi_meta["pageid"]
    if "title" in wikiapi_meta:
        meta["title"] = wikiapi_meta["title"]
    if "revisions" in wikiapi_meta:
        if "timestamp" in wikiapi_meta["revisions"][0]:
            meta["timestamp"] = wikiapi_meta["revisions"][0]["timestamp"]
        meta["_wikitext_bytes"] = len(
            wikiapi_meta["revisions"][0]["slots"]["main"]["content"]
        )

    # @TODO maybe add categories

    return meta


def wiki_as_base_request(
    title: str,
    # template_key: str,
) -> tuple:
    """wiki_as_base_request

    @deprecated Use WikitextAsData()
    """
    # Inspired on https://github.com/earwig/mwparserfromhell example
    # Demo https://wiki.openstreetmap.org/wiki/Special:ApiSandbox#action=query&format=json&prop=revisions&list=&titles=User%3AEmericusPetro%2Fsandbox%2FWiki-as-base&formatversion=2&rvprop=ids%7Ctimestamp%7Cflags%7Ccomment%7Cuser%7Ccontent&rvslots=main&rvlimit=1
    params = {
        "action": "query",
        # "prop": "revisions",
        "prop": "revisions|categories|templates",
        # "rvprop": "content",
        "rvprop": "content|timestamp",
        "rvslots": "main",
        "redirects": "1",  # redirects=1
        # "rvlimit": 1,
        "titles": title,
        "format": "json",
        "formatversion": "2",
    }

    try:
        headers = {"User-Agent": USER_AGENT}
        req = requests.get(WIKI_API, headers=headers, params=params)

        res = req.json()
        revision = res["query"]["pages"][0]["revisions"][0]
        wikiapi_meta = res["query"]["pages"][0]
        wikitext = revision["slots"]["main"]["content"]
    except (ValueError, KeyError):
        return (None, None)

    return (wikitext, wikiapi_meta)


def wiki_as_base_raw(wikitext: str) -> dict:
    return wikitext


# class Wikitext2Zip:
class WikiAsBase2Zip:
    # wab_jsonld: dict
    # file_and_data: dict

    def __init__(
        self, wab_jsonld: dict, verbose: bool = False, _next_release: bool = False
    ) -> None:
        self.wab_jsonld = None
        self.file_and_data = None

        self.wab_jsonld = wab_jsonld
        self.file_and_data = {}

        if verbose:
            self.file_and_data["wikiasbase.jsonld"] = json.dumps(
                wab_jsonld, ensure_ascii=False, indent=2
            )
        # self.file_and_data["teste.txt"] = "# filename = teste.txt"
        # self.file_and_data["teste.csv"] = "# filename = teste.csv"

        # if _next_release:
        #     data_raw_key = "data"
        # else:
        #     data_raw_key = "data_raw"

        for item in self.wab_jsonld["data"]:
            filename = None
            content = None

            # print("test data init", file=sys.stderr)

            if "wtxt:literalData" in item:
                content = item["wtxt:literalData"]

            # print(item.__dict__, file=sys.stderr)
            # @TODO improve this check to determine in file format
            # if "@id" in item and item["@id"].find(".") > -1:
            if (
                "wtxt:suggestedFilename" in item
                and item["wtxt:suggestedFilename"].find(".") > -1
            ):
                filename = item["wtxt:suggestedFilename"]
            elif (
                "wtxt:uniqueFilename" in item
                and item["wtxt:uniqueFilename"].find(".") > -1
            ):
                filename = item["wtxt:uniqueFilename"]

            # Tables need further encoding
            if item["@type"] == "wtxt:Table":
                # if "_errors" in item and len(item["_errors"]):
                #     continue

                # @TODO improve the algoritm for tables

                if (
                    "wtxt:suggestedFilename" in item
                    and item["wtxt:suggestedFilename"].find(".") > -1
                ):
                    filename = item["wtxt:suggestedFilename"]
                elif (
                    "wtxt:uniqueFilename" in item
                    and item["wtxt:uniqueFilename"].find(".") > -1
                ):
                    filename = item["wtxt:uniqueFilename"]
                # else:
                #     if "@id" in item:
                #         filename = item["@id"] + ".csv"
                #     else:
                #         continue
                # print("stargint table... filename " + filename, file=sys.stderr)
                output = io.StringIO()
                writer = csv.writer(output)

                # writer.writerow(item["header"])
                for line in item["wtxt:tableData"]:
                    writer.writerow(line)

                content = output.getvalue()
            # print("test filename " + filename, file=sys.stderr)
            # print("test content" + type(content), file=sys.stderr)
            if filename is not None and content is not None:
                # print("saved! filename " + filename, file=sys.stderr)
                self.file_and_data[filename] = content

    def output(self, zip_path: str = None):
        if zip_path:
            if isinstance(zip_path, str) and os.path.isfile(zip_path):
                os.remove(zip_path)

            with zipfile.ZipFile(
                zip_path, "a", zipfile.ZIP_DEFLATED, False
            ) as zip_file:
                for file_name, file_data in self.file_and_data.items():
                    zip_file.writestr(file_name, file_data)

            return zip_path
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(
                zip_buffer, "a", zipfile.ZIP_DEFLATED, False
            ) as zip_file:
                for file_name, file_data in self.file_and_data.items():
                    zip_file.writestr(file_name, file_data)

            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            # return str(zip_buffer.getvalue())


def wikitext_item_as_file(jsonld_object: dict) -> str:
    if not jsonld_object or not isinstance(jsonld_object, dict):
        raise SyntaxError("wikitext_item_as_file invalid type")

    if "wtxt:literalData" in jsonld_object:
        return jsonld_object["wtxt:literalData"]
    else:
        # TODO improve this part
        return json.dumps(jsonld_object, ensure_ascii=False, indent=2)


class WikitextAsData:
    """Main class to deal with conversion from Wikitext to linked data"""

    wikitext: str
    api_response: dict
    errors: list
    is_fetch_required: bool
    _wikiapi_meta: dict
    _req_params: dict
    _req_params_rest: dict
    _req_params_wb: dict
    _req_params_wb_rest: dict
    _reloaded: bool
    _mode: str = "wikitext"  # wikitext, wikibase
    # _filters: dict
    _filters: WikitextOutputFilter = None

    # # The individual resources to add on the JSON-LD data field
    _resources: list

    def __init__(self, api_params: dict = None, filters: dict = None) -> None:
        """Initialize

        Instead of defining api_params, consider use set_wikitext() or
        set_titles

        Args:
            api_params (dict, optional): (advanced use)customize default_params.
                                         Defaults to None.
        """

        # self._filters = dict

        default_params = {
            "action": "query",
            # "prop": "revisions",
            # "prop": "revisions|categories|templates",
            "prop": "revisions|categories",
            # "rvprop": "content",
            "rvprop": "content|timestamp|user",
            # "rvprop": "content|timestamp|user|langlinks",
            "rvslots": "main",
            # "rvlimit": 1,
            # "titles": title,
            "titles": None,
            "pageids": None,
            "revids": None,
            "format": "json",
            "formatversion": "2",
        }

        default_params_wb = {
            "action": "wbgetentities",
            # "prop": "revisions",
            # "prop": "revisions|categories|templates",
            "prop": "info|sitelinks|aliases|labels|descriptions|claims|datatype|sitelinks/urls",
            # nfo%7Csitelinks%7Caliases%7Clabels%7Cdescriptions%7Cclaims%7Cdatatype%7Csitelinks%2Furls
            # "rvprop": "content",
            # "rvprop": "content|timestamp|user",
            # "rvprop": "content|timestamp|user|langlinks",
            # "rvslots": "main",
            # "rvlimit": 1,
            # "titles": title,
            # "titles": None,
            # "pageids": None,
            # "revids": None,
            "ids": None,
            "format": "json",
            "formatversion": "2",
        }

        # @TODO maybe remove this part later
        ## prop=pageprops, prop=wbentityusage (example from Key:maxspeed)
        # "pageprops": {
        #     "displaytitle": "Key:maxspeed",
        #     "wikibase_item": "Q414"
        # },
        # "wbentityusage": {
        #     "Q13": {
        #         "aspects": [
        #             "C.P16",
        #             "C.P19",
        #             "C.P21",
        #             "L.en"
        #         ]
        #     },
        #     "Q414": {
        #         "aspects": [
        #             "C",
        #             "D.cs",
        #             "D.de",
        #             "D.en",
        #             "D.es",
        #             "D.fi"
        #         ]
        #     }
        # }

        if api_params is not None:
            default_params.update(api_params)

        self._req_params = default_params
        self._req_params_rest = {
            "titles": None,
            "pageids": None,
            "revids": None,
        }
        self._req_params_wb = default_params_wb
        self._req_params_wb_rest = {"ids": None}

        # @TODO deal better with reset of the class to avoid reuse
        self.wikitext = None
        self.api_response = None
        self.errors = []
        self.is_fetch_required = None
        self.is_fetch_incomplete = None
        self.is_verbose = False
        self._last_fetch_from_cache = None
        self._last_fetch_expired = None
        self._wikiapi_meta = None
        self._reloaded = None
        self._resources = []

    def _add_resource(self, resource: dict):
        self._resources.append(resource)

    # def _pagination(self, pages: Union[list, str]):
    def _pagination(self, pages: str) -> Tuple(str, str):
        parts = pages.split("|")

        # return pages
        # WTXT_PAGE_LIMIT = 9999999999

        if len(parts) <= WTXT_PAGE_LIMIT:
            return pages, None
        else:
            # @TODO implement offset
            # @TODO implement offset and WTXT_PAGE_LIMIT without env vars
            # @TODO add note on generated JSON-LD about being paginated result
            sliced = parts[0:WTXT_PAGE_LIMIT]
            rest = parts[WTXT_PAGE_LIMIT:]
            return "|".join(sliced), "|".join(rest)

    def _request_api(self):
        # Reset values
        self.wikitext = None
        self._wikiapi_meta = None

        # @TODO refactor this part to allow fetch several pages at once

        res = None

        try:
            headers = {"User-Agent": USER_AGENT}
            req = requests.get(WIKI_API, headers=headers, params=self._req_params)
            res = req.json()
            # https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html
            self._last_fetch_from_cache = req.from_cache
            self._last_fetch_expired = req.is_expired
        except Exception as err:
            # sys.stderr.write(f"{err}\n")
            self.errors.append(f"_request_api get {err}")
            # print(err)
            pass

        if res:
            try:
                # headers = {"User-Agent": USER_AGENT}
                # req = requests.get(WIKI_API, headers=headers, params=self._req_params)

                # res = req.json()
                revision = res["query"]["pages"][0]["revisions"][0]
                wikiapi_meta = res["query"]["pages"][0]
                wikitext = revision["slots"]["main"]["content"]

                self.api_response = res
                self.wikitext = wikitext
                self._wikiapi_meta = wikiapi_meta
            except (ValueError, KeyError) as err:
                # return (None, None)
                # os.sys
                # sys.stderr.write(f"{err}\n")
                self.errors.append(f"_request_api key error (some item not found?)")
                self.errors.append(res)
                # print(err)
                pass

        if self.api_response is not None:
            self._request_api_post()

        # return (wikitext, wikiapi_meta)

    def _request_api_post(self):
        # # Initialize some checks
        # @TODO finish the refactoring of this part
        template_keys = WIKI_INFOBOXES.splitlines()
        syntaxhighlight_langs = WIKI_DATA_LANGS.splitlines()

        wsite = WikisiteContext(ns=WIKI_NS)

        for page in self.api_response["query"]["pages"]:
            wpage = WikipageContext(
                wikitext=page["revisions"][0]["slots"]["main"]["content"],
                pageid=page["pageid"],
                title=page["title"],
                user=page["revisions"][0]["user"],
                timestamp=page["revisions"][0]["timestamp"],
            )
            self._resources.extend(parse_all(wpage, wsite, self._filters))
            continue

        return True

    def get(self, key: str, strict: bool = True):
        if key in self.__dict__:
            return self.__dict__[key]

        if strict:
            raise ValueError(f"WikitextAsData key [{key}]?")

    # def get_singlefile(self, filename_hint: str) -> Tuple(str, list, list):
    def get_singlefile(self, filename_hint: str) -> Tuple:
        file_mached = False
        list_fileids = []
        list_named = []
        # list_namesuggested = []
        list_ambiguous = set()

        if not self._reloaded:
            self.prepare()

        if self.is_success():
            for item in self._resources:
                if "wtxt:uniqueFilename" in item:
                    list_fileids.append(item["wtxt:uniqueFilename"])

                    if item["wtxt:uniqueFilename"] == filename_hint:
                        file_mached = item
                        break

                if "wtxt:suggestedFilename" in item:
                    if item["wtxt:suggestedFilename"] in list_named:
                        list_ambiguous.add(item["wtxt:suggestedFilename"])
                    else:
                        list_named.append(item["wtxt:suggestedFilename"])
                # print(item)
            # pass
            if not file_mached:
                _suggested_mached = None

                # @TODO: do a fuzzy match if don't find an near exact.
                # @TODO: mimic user giving as name the #Title_Hash of a title and get files inside
                for potential in list_named:
                    if filename_hint == potential:
                        _suggested_mached = potential
                        break

                for item in self._resources:
                    if (
                        "wtxt:suggestedFilename" in item
                        and _suggested_mached == item["wtxt:suggestedFilename"]
                    ):
                        file_mached = item
                        break

        if file_mached:
            file_mached = wikitext_item_as_file(file_mached)

        # self.is_verbose = filename_hint
        return file_mached, list_fileids, list_named, list(list_ambiguous)

    def is_success(self) -> bool:
        """is_success is remote fetch okay?

        Returns:
            bool: True if okay
        """
        return not self.errors or len(self.errors) == 0

    def output_jsonld(self):
        # Use wiki_as_base_meta_from_api

        if not self._reloaded:
            self.prepare()

        # if not self.errors:
        if self.is_success():
            # return wiki_as_base_all(self.wikitext, _next_release=True)

            _jsonld = {
                # TODO: make a permanent URL
                # "@context": "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/context.jsonld",
                "@context": _JSONLD_CONTEXT,
                # "$schema": "https://raw.githubusercontent.com/fititnt/wiki_as_base-py/main/schema.json",
                "$schema": _JSONSCHEMA,
                # Maybe move @type out here
                "@type": "wtxt:DataCollection",
                # @TODO implement errors
                # "data": None,
                "data": self._resources,
                # "meta": {
                #     '_source': None
                # }
            }
            return _jsonld

        else:
            # @TODO filter better the errors, in special the ones from API
            return {"error": self.errors}

    def output_jsonseq(self):
        # @see https://datatracker.ietf.org/doc/html/rfc7464

        if not self._reloaded:
            self.prepare()

        # if not self.errors:
        if self.is_success():
            # return wiki_as_base_all(self.wikitext, _next_release=True)

            for item in self._resources:
                # print("␞" + json.dumps(item, ensure_ascii=False), end="\n", file=os.stdout)
                # sys.stdout.write("␞" + json.dumps(item, ensure_ascii=False) + "\n")
                item_str = json.dumps(item, ensure_ascii=False)

                sys.stdout.write("\x1e" + item_str + "\n")
                # print(json.dumps(wtdata.output_jsonld(), ensure_ascii=False, indent=2))
            # return _jsonld

        else:
            # @TODO filter better the errors, in special the ones from API
            # return {"error": self.errors}
            raise SyntaxError({"error": self.errors})

    def output_zip(self, zip_path: str = None) -> str:
        """output_zip Output as zip (either raw data or path to output)

        _extended_summary_

        Args:
            zip_path (str, optional): The path to save on disk. Defaults to None.

        Returns:
            str: Either the raw zip data (if zip_path is None) or the
                 path itself
        """
        result = False

        if not self._reloaded:
            self.prepare()

        try:
            wabzip = WikiAsBase2Zip(
                self.output_jsonld(), verbose=True, _next_release=True
            )
            result = wabzip.output(zip_path)
        except Exception as err:
            # sys.stderr.write(f"{err}\n")
            self.errors.append(f"_request_api get {err}")
            # print(err)
            # pass

        return result

    def prepare(self):
        """prepare prepare data and/or make expensive calls"""

        if self.is_fetch_required is True or (
            self.is_fetch_required is None and self._req_params["titles"] is not None
        ):
            self._request_api()
        else:
            # We will simulate an API request
            self.api_response = {
                "query": {
                    "pages": [
                        {
                            "pageid": 0,
                            "title": "stdin",
                            "revisions": [
                                {
                                    "user": "stdin",
                                    "timestamp": datetime.datetime.now().isoformat(),
                                    "slots": {"main": {"content": self.wikitext}},
                                }
                            ],
                        }
                    ]
                }
            }
            # Now, we can continue with post API :)
            self._request_api_post()

        if self.is_fetch_incomplete:
            if self._req_params_rest["pageids"] is not None:
                self.set_pageids(self._req_params_rest["pageids"])

            elif self._req_params_rest["revids"] is not None:
                self.set_revids(self._req_params_rest["revids"])

            elif self._req_params_rest["titles"] is not None:
                self.set_titles(self._req_params_rest["titles"])
            else:
                raise NotImplemented

            # Move this to somewhere else
            if self.is_verbose:
                print(
                    f"loop... Cached: [{self._last_fetch_from_cache}] Expired: [{self._last_fetch_expired}] delay if not cached [{delay_consecutive_request()}]",
                    file=sys.stderr,
                )

            if not self._last_fetch_from_cache:
                time.sleep(delay_consecutive_request())

            return self.prepare()

        self._reloaded = True

        return self

    # def set_filters(self, filters: dict):
    def set_filters(self, item_type: str = None, item_id: str = None) -> None:
        # self.item_type = item_type
        # self.item_id = item_id
        # pass
        # if filters:
        filters = WikitextOutputFilter(item_type=item_type, item_id=item_id)

        self._filters = filters
        return self

    def set_pageids(self, pageids: str):
        """set_pageids set pageids for remote call

        Args:
            pageids (str): The Pageids. Use | as separator
        """
        # self._req_params["pageids"] = self._pagination(pageids)
        (
            self._req_params["pageids"],
            self._req_params_rest["pageids"],
        ) = self._pagination(pageids)

        # If user define pageids directly, we assume wants remote call and
        # unset titles and revids
        self.is_fetch_required = True
        self.is_fetch_incomplete = bool(self._req_params_rest["pageids"])

        if "titles" in self._req_params:
            del self._req_params["titles"]
        if "revids" in self._req_params:
            del self._req_params["revids"]

        return self

    def set_pages_autodetect(self, pages_auto: str):
        """set_pages_autodetect autodetect set_pageids() or set_titles()

        Args:
            pageids (str): Strings to autodetect. Use | as separator
        """

        pages_auto_norm = pages_auto.strip()

        if pages_auto_norm.startswith("Category:"):
            return self.set_pages_from_category(pages_auto_norm)

        parts = pages_auto_norm.split("|")
        for part in parts:
            # Any value not fully numeric means we assume are titles
            if not part.isnumeric():
                return self.set_titles(pages_auto_norm)

        return self.set_pageids(pages_auto_norm)

    def set_pages_from_category(self, category_auto: str):
        cat = WikitextPagesFromCategory()
        if not cat.set_category_autodetect(category_auto).prepare().is_success():
            self.errors.append(cat.errors)
        else:
            pageids_str = "|".join(map(str, cat.get_pageids()))
            # pageids_str = cat.get_pageids().join("|")
            self.set_pageids(pageids_str)
        return self

    def set_revids(self, revids: str):
        """set_revids set revision IDs for remote call

        Args:
            revids (str): The Revision IDs. Use | as separator
        """
        self._req_params["revids"], self._req_params_rest["revids"] = self._pagination(
            revids
        )

        # If user define revids directly, we assume wants remote call and
        # unset pageids and titles
        self.is_fetch_required = True
        self.is_fetch_incomplete = bool(self._req_params_rest["revids"])
        del self._req_params["pageids"]
        del self._req_params["titles"]

        return self

    def set_titles(self, titles: str):
        """set_pageids set page titles for remote call

        Args:
            pageids (str): The titles. Use | as separator
        """
        # self._req_params["titles"] = self._pagination(titles)
        self._req_params["titles"], self._req_params_rest["titles"] = self._pagination(
            titles
        )

        # If user define titles directly, we assume wants remote call and
        # unset pageids and revids
        self.is_fetch_required = True
        self.is_fetch_incomplete = bool(self._req_params_rest["titles"])
        del self._req_params["pageids"]
        del self._req_params["revids"]

        return self

    def set_verbose(self, is_verbose: bool = True):
        self.is_verbose = is_verbose
        return self

    def set_wikibaseids(self, wikibaseids: str):
        self._mode = "wikibase"

        self._req_params_wb["ids"], self._req_params_rest["ids"] = self._pagination(
            wikibaseids
        )

        return self

    def set_wikitext(self, wikitext: str):
        """set_wikitext set Wikitext directly instead of make API request

        Potential use: for piped in content

        Args:
            wikitext (str): the Wikitext
        """
        self.wikitext = wikitext

        # If user define wikitext directly, we assume no remote call is need
        self.is_fetch_required = False
        return self


# class WikibaseInternalJSONAsData(WikitextAsData):
#     pass

# class Wikipage:
#     pass


class WikitextGenericPart(ABC):
    """WikitextGenericPart abstract class for parts of a page"""

    pass
    # wikitext: str
    # wikipage: Wikipage

    # def set_wikitext(self, wikitext: str):
    #     return self

    # def set_wikipage(self, wikipage: Wikipage):

    #     return self


# @TODO implement WikitextDescriptionList
class WikitextDescriptionList(WikitextGenericPart):
    """WikitextDescriptionList

    @see https://en.wikipedia.org/wiki/Help:Wikitext#Lists
    @see https://html.spec.whatwg.org/multipage/grouping-content.html#the-dl-element


    @example
    = Heading 1 =
    == Heading 2 ==
    === Heading 3 ===
    ==== Heading 4 ====
    ===== Heading 5 =====
    ====== Heading 6 ======
    """

    wikimarkup: str

    def __init__(self, wikitext: str) -> None:
        self.wikimarkup = wikitext


class WikitextHeading(WikitextGenericPart):
    """WikitextHeading

    @see https://en.wikipedia.org/wiki/Help:Wikitext#Sections
    @see https://html.spec.whatwg.org/multipage/dom.html#heading-content

    @example
    = Heading 1 =
    == Heading 2 ==
    === Heading 3 ===
    ==== Heading 4 ====
    ===== Heading 5 =====
    ====== Heading 6 ======
    """

    wikimarkup: str

    def __init__(self, wikitext: str) -> None:
        self.wikimarkup = wikitext

    def get_headings(self) -> str:
        result = []
        lines = self.wikimarkup.splitlines()
        for line in lines:
            _line = line.strip()

            if not _line.startswith("=") or not _line.endswith("="):
                continue

            test_h1 = re.match("^=\s?(?P<heading>(?:[^=].)*)\s?=$", _line)
            if test_h1:
                result.append("<h1>" + test_h1.group("heading").strip() + "<h1>")
                continue

            test_h2 = re.match("^==\s?(?P<heading>(?:[^=].)*)\s?==$", _line)
            if test_h2:
                result.append("<h2>" + test_h2.group("heading").strip() + "<h2>")
                continue

            test_h3 = re.match("^===\s?(?P<heading>(?:[^=].)*)\s?===$", _line)
            if test_h3:
                result.append("<h3>" + test_h3.group("heading").strip() + "<h3>")
                continue

            test_h4 = re.match("^====\s?(?P<heading>(?:[^=].)*)\s?====$", _line)
            if test_h4:
                result.append("<h4>" + test_h4.group("heading").strip() + "<h4>")
                continue

            test_h5 = re.match("^=====\s?(?P<heading>(?:[^=].)*)\s?=====$", _line)
            if test_h5:
                result.append("<h5>" + test_h5.group("heading").strip() + "<h5>")
                continue

            test_h6 = re.match("^======\s?(?P<heading>(?:[^=].)*)\s?======$", _line)
            if test_h6:
                result.append("<h6>" + test_h6.group("heading").strip() + "<h6>")
                # continue

        return "\n".join(result)

    def get_outline(self) -> str:
        headings = self.get_headings()
        return "<article>\n" + headings + "</article>"


# Two example queries
# - https://wiki.openstreetmap.org/w/api.php?action=query&generator=categorymembers&gcmtitle=Category:External_reference_tag&prop=info
# - https://wiki.openstreetmap.org/w/api.php?action=query&cmtitle=Category:External_reference_tag&list=categorymembers&format=json&formatversion=2
#  - Web preview
#    - https://wiki.openstreetmap.org/wiki/Special:ApiSandbox#action=query&format=json&prop=&list=categorymembers&continue=-%7C%7C&formatversion=2&cmtitle=Category%3AExternal_reference_tag&cmcontinue=page%7C4b45593a4e4554574f524b3a57494b4944415441%7C186683
#    - https://wiki.openstreetmap.org/w/api.php?action=query&format=json&prop=&list=categorymembers&continue=-%7C%7C&formatversion=2&cmtitle=Category%3AExternal_reference_tag&cmcontinue=page%7C4b45593a4e4554574f524b3a57494b4944415441%7C186683&cmlimit=500
# - Category:Tagging_Mistakes
#   - https://wiki.openstreetmap.org/wiki/Special:ApiSandbox#action=query&format=json&prop=&list=categorymembers&continue=-%7C%7C&formatversion=2&cmtitle=Category%3ATagging_Mistakes&cmcontinue=page%7C4b45593a4e4554574f524b3a57494b4944415441%7C186683&cmlimit=500
class WikitextPagesFromCategory(WikitextGenericPart):
    """Return page IDs from category name

    @see https://www.mediawiki.org/wiki/API:Categorymembers

    For openstreetap categories:
    https://wiki.openstreetmap.org/wiki/Special:Categories
    """

    errors: list
    _pageids: list
    _req_params: dict
    _is_done: bool

    def __init__(self, api_params: dict = None) -> None:
        # @see https://www.mediawiki.org/wiki/API:Categorymembers
        default_params = {
            "action": "query",
            "list": "categorymembers",
            "cmprop": "ids|title|timestamp",
            "cmlimit": "500",
            "cmtitle": None,
            "cmpageid": None,
            "format": "json",
            "formatversion": "2",
        }

        if api_params is not None:
            default_params.update(api_params)

        self.errors = []
        self._pageids = []
        self._req_params = default_params
        self._is_done = False

    def _api_request(self):
        res = None

        try:
            headers = {"User-Agent": USER_AGENT}
            req = requests.get(WIKI_API, headers=headers, params=self._req_params)
            res = req.json()
        except Exception as err:
            # sys.stderr.write(f"{err}\n")
            self.errors.append(f"_request_api get {err}")
            # print(err)
            pass

        if res:
            try:
                # self._pageids = []

                for page in res["query"]["categorymembers"]:
                    self._pageids.append(page["pageid"])

            except (ValueError, KeyError) as err:
                self.errors.append(
                    f"Category _request_api key error (some item not found?)"
                )
                self.errors.append(res)

        self._is_done = True

    def prepare(self):
        if self._is_done is False:
            self._api_request()
        return self

    def get_pageids(self) -> list:
        if self.is_success():
            return self._pageids
        return False

    def is_success(self) -> bool:
        """is_success is remote fetch okay?

        Returns:
            bool: True if okay
        """
        return self._is_done is True and (not self.errors or len(self.errors) == 0)

    def set_category_autodetect(self, category_auto: str):
        """set_category_autodetect detect if cmtitle or cmpageid

        Args:
            category_auto (str): String
        """

        if category_auto.isnumeric():
            self._req_params["cmpageid"] = category_auto
            del self._req_params["cmtitle"]
        else:
            self._req_params["cmtitle"] = category_auto
            del self._req_params["cmpageid"]

        return self


class WikitextTable(WikitextGenericPart):
    """Abstract Syntax Tree of Wiki Markup table

    See https://en.wikipedia.org/wiki/Help:Basic_table_markup

    Markup	Name
    {|	Table start
    |+	Table caption
    |-	Table row
    !	Header cell
    !!	Header cell (on the same line)
    |	Data cell
    ||	Data cell (on the same line)
    |	Attribute separator
    |}	Table end

    @TODO maybe implement syntax of CSVW? https://w3c.github.io/csvw/syntax/
    """

    wikimarkup: str

    tables_potential: list = None
    tables: list = None

    def __init__(self, wikimarkup: str) -> None:
        self.wikimarkup = wikimarkup
        self.tables_potential = []
        self.tables = []
        self._init_potential_tables()

    def _init_potential_tables(self):
        reg_filename = re.compile(
            # '\{\| class="wikitable[^\}]+\|\}', flags=re.M | re.S | re.U
            "\{\| class=[\"'](?:[\w][^'\"]*\s)?wikitable[^\}]+\|\}",
            flags=re.M | re.S | re.U,
        )

        items = re.findall(reg_filename, self.wikimarkup)
        self.tables_potential = items
        for item in self.tables_potential:
            parsed = self.parse_table(item)
            if parsed is not None and len(parsed["_errors"]) == 0:
                self.tables.append(parsed)

    def parse_table(self, wikimarkup_table: str) -> dict:
        meta = {
            "caption": None,
            "header": [],
            "data": [],
            "_is_complete": False,  # Header and Rows have same length?
            "_errors": [],
        }

        lines = wikimarkup_table.splitlines()
        if not lines[0].startswith("{|") or not lines[-1].startswith("|}"):
            return None
        lines.pop(0)
        lines.pop()

        # for line in lines:
        # is_row = True
        while len(lines):
            line = lines.pop(0).strip()

            if line.startswith("|+"):
                _regresult = re.search("\|\+\s?(?P<caption>.*)", line)
                if _regresult:
                    meta["caption"] = _regresult.group("caption")
                else:
                    meta["_errors"].append("caption")
                continue

            # Header
            # @TODO fix this part because sometimes can start without space
            #       however it must not start with |- |} |+
            # if line.startswith("! "):
            if line.startswith("!"):
                if line.find("!!") > 2:
                    meta["header"] = list(
                        # map(lambda cell: cell.strip(), line.lstrip("! ").split("!!"))
                        map(self.parse_table_cellvalue, line.lstrip("! ").split("!!"))
                    )
                # if line.startswith("! ") and line.find("!!") == -1:
                else:
                    _header = []

                    while line and not line.startswith("|-"):
                        _header.append(self.parse_table_cellvalue(line.lstrip("! ")))
                        line = lines.pop(0).strip() if len(lines) > 0 else None

                    meta["header"] = _header
                continue

            # Row data
            # @TODO fix this part because sometimes can start without space
            #       however it must not start with |- |} |+
            # if line.startswith("| "):
            if line.startswith("|") and not line.startswith(("|+", "|-", "|}")):
                if line.find("||") > 2:
                    meta["data"].append(
                        list(
                            map(
                                self.parse_table_cellvalue,
                                line.lstrip("| ").split("||"),
                            )
                        )
                    )
                # if line.startswith("| ") and line.find("||") == -1:
                else:
                    _row = []

                    while line and not line.startswith("|-"):
                        _row.append(self.parse_table_cellvalue(line.lstrip("| ")))
                        line = lines.pop(0).strip() if len(lines) > 0 else None

                    meta["data"].append(_row)
                continue

            # break

        header_len = len(meta["header"])
        row_len = len(meta["data"][0]) if len(meta["data"]) > 0 else -1
        row_len_mismatch = False
        if len(meta["data"]) > 0:
            for row in meta["data"]:
                if len(row) != row_len:
                    row_len_mismatch = True
                    break
        if row_len_mismatch is False and row_len > 0 and row_len == header_len:
            meta["_is_complete"] = True
        else:
            meta["_errors"].append("incomplete table")

        return meta

    def parse_table_cellvalue(self, formatted_value: str):
        val = formatted_value

        # style="color: red" | row1cell1
        if val.find(" | ") > -1:
            parts = val.split(" | ")
            val = parts[1]

        return val.strip()

    def get_debug(self):
        debug = {"tables_potential": self.tables_potential, "tables": self.tables}
        return debug

    def get_tables(self, strict: bool = False) -> list:
        tables = []

        # @TODO enable strict=True by default

        for item in self.tables:
            if not strict or (
                len(item["_errors"]) == 0 and item["_is_complete"] == True
            ):
                tables.append(item)

        return tables


class WikitextTemplate(WikitextGenericPart):
    def __init__(self) -> None:
        pass
