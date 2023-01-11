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
import wikitextparser as wtp


def parse_sections(wikitext: str):
    return wtp.parse(wikitext).sections


def parse_tables(wikitext: str):
    return wtp.parse(wikitext).tables


def wtxt_text_corpus(wikitext: str) -> str:
    # @TODO remove <syntaxhighlight> and <source> blocks
    tcorpus = wtp.remove_markup(wikitext)
    return tcorpus
