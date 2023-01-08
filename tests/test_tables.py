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

    # wmt = wiki_as_base.WikitextTable(PERFECT_TABLE)
    # wmt = wiki_as_base.WikitextTable(PERFECT_TABLE_DOUBLEMARKS)
    wmt = wiki_as_base.WikitextTable(PERFECT_TABLE_STYLE)

    tables = wmt.get_tables()

    print(wmt.get_tables())
    # assert False

    assert len(tables) == 1
    # assert False
