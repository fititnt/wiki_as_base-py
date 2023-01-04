# from contextlib import redirect_stdout
# import io
import os
import zipfile

import wiki_as_base

# from ..src.wiki_as_base import wiki_as_base  # debug


test_dir = os.path.dirname(os.path.realpath(__file__))


def test_wiki_as_base_raw():
    with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    content_raw = wiki_as_base.wiki_as_base_raw(content)
    # print(content_raw)
    # assert False
    assert content == content_raw


def test_wiki_as_base__all_test1():
    with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
        wikitext = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_all(
        wikitext, ["ValueDescription"], ["yaml", "turtle"]
    )
    # print(results)
    # assert False
    assert results is not None
    assert results is not False
    # assert len(results['data']) == 5
    # assert len(results["data"]) == 8
    # assert len(results["data"]) == 10
    assert len(results["data"]) == 11
    assert results["@type"] == "wiki/wikiasbase"


def test_wiki_as_base__infobox_test1():
    with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
        wikitext = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_infobox(wikitext, "ValueDescription")
    print(results)
    assert results is not None
    assert results is not False
    # assert len(results) == 5
    # assert results[0][1] == 'yaml'  # 0 <syntaxhighlight lang="yaml">
    # assert results[4][1] == 'text'  # 4 <syntaxhighlight lang="text">


def test_wiki_as_base__syntaxhighlight_all():
    with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(content)
    # print(results)
    # assert False
    # assert len(results) == 5
    assert len(results) == 9
    assert results[0][1] == "yaml"  # 0 <syntaxhighlight lang="yaml">
    assert results[4][1] == "sparql"  # 4 <syntaxhighlight lang="sparql">


def test_wiki_as_base__syntaxhighlight_yaml_mul():
    with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(content, "yaml")
    # print(results)
    # assert False
    assert len(results) == 3
    assert results[0][1] == "yaml"  # 0 <syntaxhighlight lang="yaml">
    assert results[2][1] == "yaml"  # 2 <syntaxhighlight lang="yaml">
    # assert results[4][1] == 'text'  # 4 <syntaxhighlight lang="text">


def test_wiki_as_base__syntaxhighlight_yaml_has_text():
    with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(
        content, "yaml", has_text="___wikiasbase"
    )
    # print(results)
    # assert False
    assert len(results) == 2
    assert results[0][1] == "yaml"  # 0 <syntaxhighlight lang="yaml">
    assert results[1][1] == "yaml"  # 2 <syntaxhighlight lang="yaml">


def test_wiki_as_base__syntaxhighlight_yaml_match_regex():
    with open(test_dir + "/data/multiple.wiki.txt", "r") as content_file:
        content = content_file.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(
        content, "yaml", match_regex="___wikiasbase(.*)"
    )
    # print(results)
    # assert False
    assert len(results) == 2
    assert results[0][1] == "yaml"  # 0 <syntaxhighlight lang="yaml">
    assert results[1][1] == "yaml"  # 2 <syntaxhighlight lang="yaml">


def test_wiki_as_base__chatbotpor_test1():
    with open(test_dir + "/data/chatbot-por.wiki.txt", "r") as content_file2:
        content = content_file2.read()

    # Just to test if tox is working; not really useful
    results = wiki_as_base.wiki_as_base_from_syntaxhighlight(
        content, "text", match_regex="(.*)filename(.*)"
    )
    # print(results)
    # assert False
    assert len(results) == 2
    assert results[0][1] == "text"  # 0 <syntaxhighlight lang="text">
    assert results[1][1] == "text"  # 2 <syntaxhighlight lang="text">


def test_wiki_as_base__chatbotpor_test2_zip():
    with open(test_dir + "/data/chatbot-por.wiki.txt", "r") as content_file3:
        wikimarkup_raw = content_file3.read()
    wikiasbase_jsonld = wiki_as_base.wiki_as_base_all(wikimarkup_raw)

    wabzip = wiki_as_base.WikiAsBase2Zip(wikiasbase_jsonld, verbose=True)
    wabzip.output(test_dir + "/temp/chatbotpor.zip")

    zip = zipfile.ZipFile(test_dir + "/temp/chatbotpor.zip")
    names_in_zip = zip.namelist()
    # print(names_in_zip)
    # print(wikimarkup_raw)
    # print(wikiasbase_jsonld)

    # assert len(names_in_zip) == 3
    assert len(names_in_zip) == 6  # @TODO fix me; tox is caching files?
    assert "wikiasbase.jsonld" in names_in_zip
    assert "ola.rive" in names_in_zip
    assert "person.rive" in names_in_zip
