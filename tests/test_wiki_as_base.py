from contextlib import redirect_stdout
import io
import os
import sys
# from wiki_as_base import *
import wiki_as_base


test_dir = os.path.dirname(os.path.realpath(__file__))


def test_wiki_as_base_raw():
    with open(test_dir + '/data/multiple.wiki.txt', 'r') as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    content_raw = wiki_as_base.wiki_as_base_raw(content)
    # print(content)
    # assert False
    assert content == content_raw
