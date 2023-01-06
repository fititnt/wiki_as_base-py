# from contextlib import redirect_stdout
# import io
import os
import zipfile

import wiki_as_base

# from ..src.wiki_as_base import wiki_as_base  # debug


test_dir = os.path.dirname(os.path.realpath(__file__))


# def test_wikitext_001():
#     with open(test_dir + "/data/chatbot-por.wiki.txt", "r") as content_file3:
#         wikitext = content_file3.read()

#     wtdata = wiki_as_base.WikitextAsData().set_wikitext(wikitext)
#     # print(content_raw)
#     # assert False
#     assert wikitext == wtdata.get('wikitext')


def test_wikitext_002():

    source_wikitext = test_dir + "/data/chatbot-por.wiki.txt"
    target_zipfile = test_dir + "/temp/chatbotpor.zip"

    with open(source_wikitext, "r") as content_file3:
        wikitext = content_file3.read()

    wtdata = wiki_as_base.WikitextAsData().set_wikitext(wikitext)
    wtdata.output_zip(target_zipfile)

    # Now we analyse the zip file
    zip = zipfile.ZipFile(test_dir + "/temp/chatbotpor.zip")
    names_in_zip = zip.namelist()

    assert len(names_in_zip) == 4
    # assert len(names_in_zip) == 6  # @TODO fix me; tox is caching files?
    assert "wikiasbase.jsonld" in names_in_zip
    assert "ola.rive" in names_in_zip
    assert "person.rive" in names_in_zip
