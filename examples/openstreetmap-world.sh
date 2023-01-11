#!/bin/bash
Editor_usage_stats

#### Categories ________________________________________________________________
# List with all https://wiki.openstreetmap.org/wiki/Special:Categories

# 58 members Category:Aeroways
wiki_as_base --input-autodetect 'Category:Aeroways' --verbose --output-zip-file ./tests/temp/Category:Aeroways.zip

#### Other _____________________________________________________________________

#wiki_as_base --input-autodetect 'Editor_usage_stats' --verbose

wiki_as_base --input-autodetect 'Editor_usage_stats' --verbose --output-zip-file ./tests/temp/Editor_usage_stats.zip

wiki_as_base --input-autodetect 'Category:OSM_API' --verbose --output-zip-file ./tests/temp/Category:OSM_API.zip
wiki_as_base --input-autodetect 'Category:Tag_descriptions_for_group_"emergencies"' --verbose --output-zip-file ./tests/temp/Category:Tag_descriptions_for_group_emergencies.zip


