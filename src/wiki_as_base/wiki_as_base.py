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
import csv
import io
import json
import os
import re
from typing import List, Union
import zipfile
import requests

_REFVER = "0.5.2"

USER_AGENT = os.getenv("USER_AGENT", "wiki-as-base/" + _REFVER)
WIKI_API = os.getenv("WIKI_API", "https://wiki.openstreetmap.org/w/api.php")

WIKI_INFOBOXES = os.getenv("WIKI_INFOBOXES", "ValueDescription\nKeyDescription")

# @TODO WIKI_INFOBOXES_IDS
WIKI_INFOBOXES_IDS = os.getenv("WIKI_INFOBOXES_IDS", "{key}={value}\n{key}")


# @TODO add other common formats on <syntaxhighlight lang="">
#       see https://pygments.org/docs/formatters/
#       see https://pygments.org/docs/lexers/
#           - Stopped on 'Lexers for .net languages'; needs check others
_default_langs = {
    "c": "c",  # what about .h?
    "css": "css",
    "c\+\+": "cpp",
    "cpp": "cpp",
    "dpatch": "dpatch",
    "diff": "diff",
    "udiff": "diff",
    "html": "html",
    "latex": "tex",
    "tex": "tex",
    "json": "json",
    "python": "py",
    # "raw": "raw",
    # "tokens": "raw",
    "sparql": "rq",
    "sql": "sql",
    "svg": "svg",
    "text": "txt",
    "turtle": "ttl",
    "toml": "toml",
    "terraform": "tf",
    "tf": "tf",
    "xml": "xml",
    "yaml": "yml",
}

# WIKI_DATA_LANGS = os.getenv("WIKI_DATA_LANGS", "yaml\nturtle\ntext\ncpp\nsparql\nsql")
WIKI_DATA_LANGS = os.getenv("WIKI_DATA_LANGS", "\n".join(_default_langs.keys()))
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

    wmt = WikiMarkupTableAST(wikitext)
    tables = wmt.get_tables()
    if tables and len(tables) > 0:
        index = 1
        for table in tables:
            _tbl = {"@type": "wiki/data/table", "@id": f"t{index}"}
            # table["@type"] = "wiki/data/table"
            # table["@id"] = f"t{index}"
            _tbl.update(table)
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


class WikiAsBase2Zip:
    wab_jsonld: dict = {}
    file_and_data: dict = {}

    def __init__(self, wab_jsonld: dict, verbose: bool = False) -> None:
        self.wab_jsonld = wab_jsonld
        if verbose:
            self.file_and_data["wikiasbase.jsonld"] = json.dumps(
                wab_jsonld, ensure_ascii=False, indent=2
            )
        # self.file_and_data["teste.txt"] = "# filename = teste.txt"
        # self.file_and_data["teste.csv"] = "# filename = teste.csv"

        for item in self.wab_jsonld["data"]:
            filename = None
            content = None
            # @TODO improve this check to determine in file format
            if "@id" in item and item["@id"].find(".") > -1:
                filename = item["@id"]
                if "data_raw" in item:
                    content = item["data_raw"]

            elif "@id" in item and item["@type"] == "wiki/data/table":
                if "_errors" in item and len(item["_errors"]):
                    continue
                filename = item["@id"] + ".csv"

                output = io.StringIO()
                writer = csv.writer(output)

                writer.writerow(item["header"])
                for line in item["data"]:
                    writer.writerow(line)

                content = output.getvalue()

            if filename is not None and content is not None:
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


class WikiMarkupTableAST:
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

    tables_potential: list = []
    tables: list = []

    def __init__(self, wikimarkup: str) -> None:
        self.wikimarkup = wikimarkup
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
