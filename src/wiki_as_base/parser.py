#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  parser.py
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

# https://github.com/5j9/wikitextparser
from typing import List, Union
from dataclasses import dataclass, field
import re
import wikitextparser as wtp

from .constants import WIKI_DATA_LANGS, WIKI_TEMPLATES, _default_langs


@dataclass
class WikipageContext:
    wikitext: str
    pageid: int
    title: str
    user: str
    timestamp: str
    title_norm: str = field(init=False)

    def __post_init__(self):
        self.title_norm = self.title.replace(" ", "_")


@dataclass
class WikisiteContext:
    ns: str


@dataclass
class WikitextTemplateContext:
    name: str
    literal: str
    arguments: dict
    pagectx: WikipageContext
    # meta: dict
    local_id: str = field(init=False)

    # @TODO make this generic, not hardcoded to OpenStreetMap
    def __post_init__(self):
        # self.local_id = f'#pageid{self.pagectx.pageid}'
        # self.local_id = f"pageid{self.pagectx.pageid}"
        self.local_id = f"{self.pagectx.title_norm}"


def _headings(
    page_title: str, level_now: int, title_now: str = None, stack: list = None
):
    # if stack is None:
    if not isinstance(stack, list):
        stack = [page_title, "", "", "", "", "", "", ""]
    # return ValueError
    if level_now == 0:
        return stack
    if level_now == 1:
        stack[1] = title_now.strip()
        return [stack[0], stack[1], "", "", "", "", "", ""]
    if level_now == 2:
        stack[2] = title_now.strip()
        return [stack[0], stack[1], stack[2], "", "", "", "", ""]
    if level_now == 3:
        stack[3] = title_now.strip()
        return [stack[0], stack[1], stack[2], stack[3], "", "", "", ""]
    if level_now == 4:
        stack[4] = title_now.strip()
        return [stack[0], stack[1], stack[2], stack[3], stack[4], "", "", ""]
    if level_now == 5:
        stack[5] = title_now.strip()
        return [
            stack[0],
            stack[1],
            stack[2],
            stack[3],
            stack[4],
            stack[5],
            "",
            "",
        ]
    if level_now == 6:
        stack[6] = title_now.strip()
        return [
            stack[0],
            stack[1],
            stack[2],
            stack[3],
            stack[4],
            stack[5],
            stack[6],
            "",
        ]
    if level_now == 7:
        stack[7] = title_now.strip()
        return [
            stack[0],
            stack[1],
            stack[2],
            stack[3],
            stack[4],
            stack[5],
            stack[6],
            stack[7],
        ]
    return ["err", "err", "err", "err", "err", "err", "err", "err"]
    # return ValueError


def _parse_value(value_literal: str) -> Union[list, str]:
    """_parse_value parse value arguments of templates

    Args:
        value_literal (str): the input data

    Returns:
        Union[list, str]: if list, return list, if string, strip spaces
    """
    result = value_literal.strip()
    if len(result) > 0:
        parsed = wtp.parse(result)
        # Note: we're only get the first list; may have bugs
        wikilist = parsed.get_lists()
        if len(wikilist) > 0:
            result = list(map(lambda item: item.strip(), wikilist[0].items))

    return result


def _fileextension(extension: str) -> str:
    extension_norm = extension
    if extension in _default_langs:
        extension_norm = _default_langs[extension]

    return extension_norm


def parse_all(pagectx: WikipageContext, sitectx: WikisiteContext) -> list:
    page_data = []

    tcorpus = wtxt_text_corpus(pagectx.wikitext)
    if tcorpus:
        page_data.append(
            {
                # "@type": "wiki/outline",
                # "@type": "wtxt:DataCollectionOutline",
                "@type": "wtxt:TextCorpus",
                "@id": f"{sitectx.ns}:{pagectx.title_norm}#__textcorpus",
                "wtxt:inWikipage": f"{sitectx.ns}:{pagectx.title_norm}",
                # @TODO remove prefix outline/ from here
                #       and implement on zip output only
                "wtxt:suggestedFilename": f"corpora/{sitectx.ns}:{pagectx.title_norm}.txt",
                "wtxt:uniqueFilename": f"corpora/{sitectx.ns}_pageid{pagectx.pageid}.txt",
                "wtxt:timestamp": pagectx.timestamp,
                "wtxt:user": pagectx.user,
                # 'data_raw': outline,
                # data_raw_key: outline,
                "wtxt:literalData": tcorpus,
            }
        )

    parsed = wtp.parse(pagectx.wikitext)

    total_tables = len(parsed.tables)
    tables_counter = 0

    # hstack = None
    hstack = [pagectx.title, "", "", "", "", "", "", ""]
    for section in parsed.sections:
        # page_data.append({"title": section.title, '_nesting_level': section._nesting_level})

        title = section.title.strip() if section.title else None
        contents = section.contents

        hstack = _headings(pagectx.title, section.level, title, hstack)

        # Lets get only relevant contents for this header
        parsed_now = wtp.parse(contents)
        if len(parsed_now.sections) > 1:
            contents = parsed_now.sections[0].contents

        contents_raw = wtp.remove_markup(contents.strip())
        if len(contents_raw) == 0:
            continue

        parsed_now_again = wtp.parse(contents)

        # # print(hstack)
        # # print(type(hstack))
        # page_data.append(
        #     {
        #         "@type": "____debug",
        #         "wtxt:titleContext": "\n".join(hstack),
        #         "title": title,
        #         "level": section.level,
        #         "contents": contents,
        #         "__templates": repr(parsed_now_again.templates),
        #     }
        # )

        if len(parsed_now_again.tables):
            for table in parsed_now_again.tables:
                tables_counter += 1
                page_data.append(
                    {
                        "@type": "wtxt:Table",
                        "@id": f"{sitectx.ns}:{pagectx.title_norm}#__table{tables_counter}",
                        "wtxt:titleContext": "\n".join(hstack),
                        "wtxt:uniqueFilename": f"{sitectx.ns}_pageid{pagectx.pageid}_item{tables_counter}.csv",
                        "wtxt:tableData": table.data(),
                        # "_is_complete": True,
                        # "_errors": None,
                    }
                )

        # raise ValueError(contents)

        templates = parse_templates(contents, pagectx)
        if templates:
            for template in templates:
                # tables_counter += 1
                page_data.append(
                    {
                        "@type": "wtxt:Template",
                        "@id": f"{sitectx.ns}:Template:{template.name}#{template.local_id}",
                        "wtxt:titleContext": "\n".join(hstack),
                        # "wtxt:uniqueFilename": f"{sitectx.ns}_pageid{pagectx.pageid}_table{index_syntax}.csv",
                        # "wtxt:uniqueFilename": f"{sitectx.ns}:Template:{template.name}#{template.local_id}",
                        # # @TODO maybe enable wtxt:literalData (if debug on)
                        # "wtxt:literalData": template.literal,
                        "wtxt:templateData": template.arguments,
                    }
                )

        index_syntax = 0
        for item in WIKI_DATA_LANGS.splitlines():
            results = wiki_as_base_from_syntaxhighlight_v2(contents, item)
            if not results:
                continue

            for result in results:
                if not result:
                    continue
                index_syntax += 1
                fileextension = _fileextension(result[1])
                if result[2]:
                    page_data.append(
                        {
                            "@type": "wtxt:PreformattedCode",
                            "wtxt:syntaxLang": result[1],
                            "wtxt:suggestedFilename": result[2],
                            "wtxt:uniqueFilename": f"{sitectx.ns}_pageid{pagectx.pageid}_item{index_syntax}.{fileextension}",
                            "wtxt:inWikipage": f"{sitectx.ns}:{pagectx.title_norm}",
                            "wtxt:literalData": result[0],
                        }
                    )
                else:
                    page_data.append(
                        {
                            "@type": "wtxt:PreformattedCode",
                            "wtxt:syntaxLang": result[1],
                            "wtxt:uniqueFilename": f"{sitectx.ns}_pageid{pagectx.pageid}_item{index_syntax}.{fileextension}",
                            "wtxt:inWikipage": f"{sitectx.ns}:{pagectx.title_norm}",
                            "wtxt:literalData": result[0],
                        }
                    )

    return page_data


def parse_sections(wikitext: str):
    return wtp.parse(wikitext).sections


def parse_tables(wikitext: str):
    return wtp.parse(wikitext).tables


def parse_templates(
    wikitext: str, pagectx: WikipageContext
) -> List[WikitextTemplateContext]:
    results = []

    parsed = wtp.parse(wikitext)
    if parsed.templates:
        for template in parsed.templates:

            if template.name.strip() not in WIKI_TEMPLATES:
                # if WIKI_TEMPLATES.find(template.name.strip()) == -1:
                # print('continue', template.name)
                continue

            # raise ValueError(WIKI_TEMPLATES, template.name.strip())
            template.normal_name
            arguments = {}
            for args in template.arguments:
                # arguments[args.name] = args.value.strip()
                arguments[args.name.strip()] = _parse_value(args.value)

            tpl = WikitextTemplateContext(
                name=template.name.strip(),
                literal=template.pformat(),
                arguments=arguments,
                pagectx=pagectx,
                # meta={
                #     "arguments": arguments,
                #     # "normal_name": template.normal_name,
                #     # "parameters": template.parameters,
                # },
            )

            # raise ValueError(template)
            # results.append(template.pformat())
            results.append(tpl)

    return results if len(results) > 0 else None


def wtxt_text_corpus(wikitext: str) -> str:
    # @TODO remove <syntaxhighlight> and <source> blocks
    tcorpus = wtp.remove_markup(wikitext)
    return tcorpus


def wiki_as_base_from_syntaxhighlight_v2(
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
