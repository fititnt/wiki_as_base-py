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

import re
from typing import List, Union

# @see https://docs.python.org/pt-br/3/library/re.html#re-objects
# @see https://github.com/earwig/mwparserfromhell
# @see https://github.com/siznax/wptools

# @see https://regex101.com/r/rwCoVw/1
# REG = re.compile('<syntaxhighlight lang=\"([a-z0-9]{2,20})\">(.*?)</syntaxhighlight>', flags='gmus')
REG_SH_GENERIC = re.compile(
    '<syntaxhighlight lang=\"(?P<lang>[a-z0-9]{2,20})\">(?P<data>.*?)</syntaxhighlight>',
    flags=re.M | re.S | re.U)


def wiki_as_base_all(
    wikitext: str,
    template_keys: List[str] = None,
    syntaxhighlight_langs: List[str] = None,
) -> dict:
    data = {
        "type": 'wikiasbase',
        "data": []
    }

    if template_keys is not None and len(template_keys) > 0:
        for item in template_keys:
            result = wiki_as_base_from_infobox(wikitext, item)
            if result:
                data['data'].append(
                    result
                )

    if syntaxhighlight_langs is not None and len(syntaxhighlight_langs) > 0:
        for item in syntaxhighlight_langs:
            result = wiki_as_base_from_syntaxhighlight(wikitext, item)
            if result:
                data['data'].append(
                    result
                )

    return data


def wiki_as_base_from_infobox(
    wikitext: str,
    template_key: str,
):
    data = {}
    data['_allkeys'] = []
    # @TODO https://stackoverflow.com/questions/33862336/how-to-extract-information-from-a-wikipedia-infobox
    # @TODO make this part not with regex, but rules.

    if wikitext.find('{{' + template_key) == -1:
        return None

    # @TODO better error handling
    if wikitext.count('{{' + template_key) > 1:
        return False

    try:
        start_template = wikitext.split('{{' + template_key)[1]
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
            if raw_line_trimmed.startswith('|'):
                key_tmp, value_tmp = raw_line_trimmed.split('=')
                key = key_tmp.strip('|').strip()
                data['_allkeys'].append(key)
                if len(raw_lines) >= index + 1:
                    if raw_lines[index + 1].strip() == '}}' or \
                            raw_lines[index + 1].strip().startswith('|'):
                        # closed
                        data[key] = value_tmp.strip()
                        # pass
                    # pass
                # pass
    except ValueError:
        return None

    # return wikitext
    return data


def wiki_as_base_from_syntaxhighlight(
        wikitext: str, lang: str = None,
        has_text: str = None,
        match_regex: str = None
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
            '<syntaxhighlight lang=\"(?P<lang>[a-z0-9]{2,20})\">(?P<data>.*?)</syntaxhighlight>',
            flags=re.M | re.S | re.U)
    else:
        reg_sh = re.compile(
            f'<syntaxhighlight lang=\"(?P<lang>{lang})\">(?P<data>.*?)</syntaxhighlight>',
            flags=re.M | re.S | re.U)

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

    # swap order
    for item in items:
        result.append((item[1].strip(), item[0]))

    return result


def wiki_as_base_meta(wikitext: str) -> dict:
    return {}


def wiki_as_base_raw(wikitext: str) -> dict:
    return wikitext
