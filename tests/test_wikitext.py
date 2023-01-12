# from contextlib import redirect_stdout
# import io
import os
import zipfile

# import wiki_as_base
from wiki_as_base import WikitextAsData

test_dir = os.path.dirname(os.path.realpath(__file__))


def test_wikitext_001_jsonld():
    source_wikitext = test_dir + "/data/multiple.wiki.txt"
    # target_zipfile = test_dir + "/temp/chatbotpor.zip"

    with open(source_wikitext, "r") as _file:
        wikitext = _file.read()

    wtxt = WikitextAsData()
    wtxt_jsonld = wtxt.set_wikitext(wikitext).output_jsonld()

    print(wtxt_jsonld)
    # assert False
    assert wtxt_jsonld is not None
    assert wtxt_jsonld is not False
    # assert len(wtxt_jsonld["data"]) == 13
    assert len(wtxt_jsonld["data"]) == 14
    assert wtxt_jsonld["@type"] == "wtxt:DataCollection"


def test_wikitext_002_zipfile():

    source_wikitext = test_dir + "/data/chatbot-por.wiki.txt"
    target_zipfile = test_dir + "/temp/chatbotpor.zip"

    with open(source_wikitext, "r") as content_file3:
        wikitext = content_file3.read()

    wtxt = WikitextAsData()
    wtxt.set_wikitext(wikitext).output_zip(target_zipfile)

    # Now we analyse the zip file
    zip = zipfile.ZipFile(target_zipfile)
    names_in_zip = zip.namelist()

    assert len(names_in_zip) == 4
    # assert len(names_in_zip) == 6  # @TODO fix me; tox is caching files?
    assert "wikiasbase.jsonld" in names_in_zip
    assert "ola.rive" in names_in_zip
    assert "person.rive" in names_in_zip
    assert "R001_wikidata.shacl.ttl" not in names_in_zip


def test_wikitext_003_zipfile():

    source_wikitext = test_dir + "/data/multiple.wiki.txt"
    target_zipfile = test_dir + "/temp/multiple.zip"

    with open(source_wikitext, "r") as content_file3:
        wikitext = content_file3.read()

    wtxt = WikitextAsData()
    wtxt.set_wikitext(wikitext).output_zip(target_zipfile)

    # Now we analyse the zip file
    zip = zipfile.ZipFile(target_zipfile)
    names_in_zip = zip.namelist()
    print(names_in_zip)

    # assert len(names_in_zip) == 7
    # assert len(names_in_zip) == 11
    assert len(names_in_zip) == 13
    assert "wikiasbase.jsonld" in names_in_zip
    assert "corpora/osmwiki:stdin.txt" in names_in_zip  # temp, may change
    assert "osmwiki_pageid0_item1.yml" in names_in_zip  # temp, may change
    assert "osmwiki_pageid0_item4.csv" in names_in_zip  # temp, may change
    assert "ola.rive" not in names_in_zip
    assert "person.rive" not in names_in_zip
    assert "R001_wikidata.shacl.ttl" in names_in_zip
    assert "R001_wikidata-valid.tdata.ttl" in names_in_zip


def test_wikitext_004_zipfile():
    # Re-testing again. Must not remember previous state from
    # test_wikitext_002_zipfile

    source_wikitext = test_dir + "/data/chatbot-por.wiki.txt"
    target_zipfile = test_dir + "/temp/chatbotpor.zip"

    with open(source_wikitext, "r") as content_file3:
        wikitext = content_file3.read()

    wtxt = WikitextAsData()
    wtxt.set_wikitext(wikitext).output_zip(target_zipfile)

    # Now we analyse the zip file
    zip = zipfile.ZipFile(target_zipfile)
    names_in_zip = zip.namelist()

    assert len(names_in_zip) == 4
    # assert len(names_in_zip) == 6  # @TODO fix me; tox is caching files?
    assert "wikiasbase.jsonld" in names_in_zip
    assert "ola.rive" in names_in_zip
    assert "person.rive" in names_in_zip
    assert "R001_wikidata.shacl.ttl" not in names_in_zip
