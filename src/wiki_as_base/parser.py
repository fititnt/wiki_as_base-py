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
from dataclasses import dataclass, field
import wikitextparser as wtp

# from .wiki_as_base import (
#     WIKI_NS,
# )


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


def _headings(level_now: int, title_now: str = None, stack: list = None):
    # if stack is None:
    if not isinstance(stack, list):
        stack = ["", "", "", "", "", "", "", ""]
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
    # hstack = None
    hstack = ["", "", "", "", "", "", "", ""]
    for section in parsed.sections:
        # page_data.append({"title": section.title, '_nesting_level': section._nesting_level})

        title = section.title.strip() if section.title else None

        hstack = _headings(section.level, title, hstack)
        # print(hstack)
        # print(type(hstack))
        page_data.append(
            {
                "_headers": "\n".join(hstack),
                "title": title,
                "level": section.level,
                "contents": section.contents,
            }
        )
        # print(section.ancestors)
        # print(section.)
        # pass

    return page_data


def parse_sections(wikitext: str):
    return wtp.parse(wikitext).sections


def parse_tables(wikitext: str):
    return wtp.parse(wikitext).tables


def wtxt_text_corpus(wikitext: str) -> str:
    # @TODO remove <syntaxhighlight> and <source> blocks
    tcorpus = wtp.remove_markup(wikitext)
    return tcorpus
