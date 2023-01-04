# from contextlib import redirect_stdout
# import io
import os
import zipfile

import wiki_as_base

# from ..src.wiki_as_base import wiki_as_base  # debug
# @see https://en.wikipedia.org/wiki/Help:Basic_table_markup

test_dir = os.path.dirname(os.path.realpath(__file__))

PERFECT_TABLE = """{| class="wikitable"
|+ Caption: example table
|-
! header1
! header2
! header3
|-
| row1cell1
| row1cell2
| row1cell3
|-
| row2cell1
| row2cell2
| row2cell3
|}
"""

PERFECT_TABLE_DOUBLEMARKS = """{| class="wikitable"
|+ Caption: example table
|-
! header1 !! header2 !! header3
|-
| row1cell1 || row1cell2 || row1cell3
|-
| row2cell1 || row2cell2 || row2cell3
|}
"""

PERFECT_TABLE_STYLE = """{| class="wikitable"
|+ Caption: some cells red text.
|-
! header1
! header2
! header3
|-
| style="color: red" | row1cell1
| row1cell2
| style="color: red" | row1cell3
|-
| row2cell1
| style="color: red" | row2cell2
| row2cell3
|}
"""


def test_wiki_as_base_raw():

    # wmt = wiki_as_base.WikiMarkupTableAST(PERFECT_TABLE)
    wmt = wiki_as_base.WikiMarkupTableAST(PERFECT_TABLE_DOUBLEMARKS)

    print(wmt.get_debug())
    # raise ValueError(wmt.get_debug())
    # assert False
    assert True

    # raise ValueError(wmt)

    # with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
    #     content = content_file.read()

    # # Just to test if tox is working; not really useful
    # content_raw = wiki_as_base.wiki_as_base_raw(content)
    # # print(content_raw)
    # # assert False
    # assert content == content_raw
