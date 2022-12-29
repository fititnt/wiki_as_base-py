# from contextlib import redirect_stdout
# import io
import os

import wiki_as_base
# from ..src.wiki_as_base import wiki_as_base  # debug


test_dir = os.path.dirname(os.path.realpath(__file__))


def test_wiki_as_base_raw():
    with open(test_dir + '/data/multiple.wiki.txt', 'r') as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    content_raw = wiki_as_base.wiki_as_base_raw(content)
    # print(content_raw)
    # assert False
    assert content == content_raw


def test_wiki_as_base__syntaxhighlight_all():
    with open(test_dir + '/data/multiple.wiki.txt', 'r') as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(content)
    # print(results)
    # assert False
    assert len(results) == 5
    assert results[0][1] == 'yaml'  # 0 <syntaxhighlight lang="yaml">
    assert results[4][1] == 'text'  # 4 <syntaxhighlight lang="text">


def test_wiki_as_base__syntaxhighlight_yaml_mul():
    with open(test_dir + '/data/multiple.wiki.txt', 'r') as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(content, 'yaml')
    # print(results)
    # assert False
    assert len(results) == 3
    assert results[0][1] == 'yaml'  # 0 <syntaxhighlight lang="yaml">
    assert results[2][1] == 'yaml'  # 2 <syntaxhighlight lang="yaml">
    # assert results[4][1] == 'text'  # 4 <syntaxhighlight lang="text">


def test_wiki_as_base__syntaxhighlight_yaml_has_text():
    with open(test_dir + '/data/multiple.wiki.txt', 'r') as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(
        content, 'yaml', has_text='___wikiasbase')
    # print(results)
    # assert False
    assert len(results) == 2
    assert results[0][1] == 'yaml'  # 0 <syntaxhighlight lang="yaml">
    assert results[1][1] == 'yaml'  # 2 <syntaxhighlight lang="yaml">


def test_wiki_as_base__syntaxhighlight_yaml_match_regex():
    with open(test_dir + '/data/multiple.wiki.txt', 'r') as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(
        content, 'yaml', match_regex='___wikiasbase(.*)')
    # print(results)
    # assert False
    assert len(results) == 2
    assert results[0][1] == 'yaml'  # 0 <syntaxhighlight lang="yaml">
    assert results[1][1] == 'yaml'  # 2 <syntaxhighlight lang="yaml">
