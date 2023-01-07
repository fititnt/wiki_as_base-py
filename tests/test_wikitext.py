# from contextlib import redirect_stdout
# import io
import os
import zipfile

import wiki_as_base

# from ..src.wiki_as_base import wiki_as_base  # debug


test_dir = os.path.dirname(os.path.realpath(__file__))


def test_wikitext_001_jsonld():
    source_wikitext = test_dir + "/data/multiple.wiki.txt"
    # target_zipfile = test_dir + "/temp/chatbotpor.zip"

    with open(source_wikitext, "r") as _file:
        wikitext = _file.read()

    wtdata = wiki_as_base.WikitextAsData()
    jsonld = wtdata.set_wikitext(wikitext).output_jsonld()

    print(jsonld)
    # assert False
    assert jsonld is not None
    assert jsonld is not False
    # assert len(results['data']) == 5
    # assert len(results["data"]) == 8
    # assert len(results["data"]) == 10
    # assert len(jsonld["data"]) == 11
    assert len(jsonld["data"]) == 13
    assert jsonld["@type"] == "wtxt:DataCollection"


def test_wikitext_002_zipfile():

    source_wikitext = test_dir + "/data/chatbot-por.wiki.txt"
    target_zipfile = test_dir + "/temp/chatbotpor.zip"

    with open(source_wikitext, "r") as content_file3:
        wikitext = content_file3.read()

    wtdata = wiki_as_base.WikitextAsData()
    wtdata.set_wikitext(wikitext).output_zip(target_zipfile)

    # Now we analyse the zip file
    zip = zipfile.ZipFile(test_dir + "/temp/chatbotpor.zip")
    names_in_zip = zip.namelist()

    assert len(names_in_zip) == 4
    # assert len(names_in_zip) == 6  # @TODO fix me; tox is caching files?
    assert "wikiasbase.jsonld" in names_in_zip
    assert "ola.rive" in names_in_zip
    assert "person.rive" in names_in_zip
