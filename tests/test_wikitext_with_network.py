# Warning: requests here migth fail because they will ask external API

import os

# import wiki_as_base
from wiki_as_base import WikitextAsData


test_dir = os.path.dirname(os.path.realpath(__file__))

# def test_wikitext_with_network_001_jsonld():
def _disabled_test_wikitext_with_network_001_jsonld():

    # def test_wikitext_with_network_001_jsonld():
    source_titles = "User:EmericusPetro/sandbox/Wiki-as-base|User:EmericusPetro/sandbox/Wiki-as-base/data-validation"

    # Both cases are expected to have same output
    # wtdata = WikitextAsData().set_titles(source_titles)
    wtxt = WikitextAsData().set_pages_autodetect(source_titles)
    wtxt_jsonld = wtxt.output_jsonld()

    print(wtxt_jsonld)
    # assert False
    assert wtxt_jsonld is not None
    assert wtxt_jsonld is not False
    assert len(wtxt_jsonld["data"]) == 18
    assert wtxt_jsonld["@type"] == "wtxt:DataCollection"


# def test_wikitext_with_network_002_jsonld():
def _disabled_test_wikitext_with_network_002_jsonld():

    source_titles = "295916|296167"

    # Both cases are expected to have same output
    # wtxt = WikitextAsData.set_titles(source_titles)
    wtxt = WikitextAsData().set_pages_autodetect(source_titles)
    wtxt_jsonld = wtxt.output_jsonld()

    print(wtxt_jsonld)
    # assert False
    assert wtxt_jsonld is not None
    assert wtxt_jsonld is not False
    assert len(wtxt_jsonld["data"]) == 18
    assert wtxt_jsonld["@type"] == "wtxt:DataCollection"


# def test_wikitext_002_zipfile():

#     source_wikitext = test_dir + "/data/chatbot-por.wiki.txt"
#     target_zipfile = test_dir + "/temp/chatbotpor.zip"

#     with open(source_wikitext, "r") as content_file3:
#         wikitext = content_file3.read()

#     wtdata = wiki_as_base.WikitextAsData().set_wikitext(wikitext)
#     wtdata.output_zip(target_zipfile)

#     # Now we analyse the zip file
#     zip = zipfile.ZipFile(test_dir + "/temp/chatbotpor.zip")
#     names_in_zip = zip.namelist()

#     assert len(names_in_zip) == 4
#     # assert len(names_in_zip) == 6  # @TODO fix me; tox is caching files?
#     assert "wikiasbase.jsonld" in names_in_zip
#     assert "ola.rive" in names_in_zip
#     assert "person.rive" in names_in_zip
