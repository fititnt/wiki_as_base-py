# This will just print the output
#    python ./examples/zip-remote-data.py

import sys
import zipfile
from wiki_as_base import WikitextAsData

wtxt = WikitextAsData().set_pages_autodetect("295916|296167")

# Both output_jsonld() and output_zip() call prepare() (which actually
# make the remote request) plus is_success() on demand.
# However the pythonic way woud be try/except
if not wtxt.prepare().is_success():
    print("error")
    print(wtxt.errors)
    sys.exit(1)

wtxt.output_zip("/tmp/wikitext.zip")

# Using Python zipfile.ZipFile, you can process the file with python
zip = zipfile.ZipFile("/tmp/wikitext.zip")

print("Files inside the zip:")
print(zip.namelist())

# @TODO improve this example on future releases
