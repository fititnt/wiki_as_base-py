# This will just print the output
#    python ./examples/explore-remote-data.py

import json
from wiki_as_base import WikitextAsData

wtxt = WikitextAsData().set_pages_autodetect("295916|296167")
wtxt_jsonld = wtxt.output_jsonld()

print(f'Total: {len(wtxt_jsonld["data"])}')

for resource in wtxt_jsonld["data"]:
    if resource["@type"] == "wtxt:Table":
        print("table found!")
        print(resource["wtxt:tableData"])

print("Pretty print full JSON output")

print(json.dumps(wtxt.output_jsonld(), ensure_ascii=False, indent=2))
