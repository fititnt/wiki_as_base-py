#!/bin/bash

# @see https://github.com/ldodds/overpass-doc
# @see https://osm-queries.ldodds.com/
# @see https://wiki.openstreetmap.org/wiki/Overpass_turbo/MapCSS

### Overpass ___________________________________________________________________

curl --silent 'https://wiki.openstreetmap.org/w/api.php?action=query&cmtitle=Category:Overpass_API&list=categorymembers&format=json' | jq '.query.categorymembers | .[] | .pageid'
# 35322
# 253043
# 104140
# 100013
# 156642
# 96046
# 141055
# 101307
# 72215
# 98438

curl --silent 'https://wiki.openstreetmap.org/w/api.php?action=query&cmtitle=Category:Overpass_API&list=categorymembers&format=json' | jq '.query.categorymembers | .[] | .pageid' | tr -s "\n" "|"
# 35322|253043|104140|100013|156642|96046|141055|101307|72215|98438|


wiki_as_base --input-autodetect '35322|253043|104140|100013|156642|96046|141055|101307|72215|98438' --output-zip-file ./tests/temp/category-overpass-api.zip

wiki_as_base --input-autodetect 'Category:Overpass_API' --output-zip-file ./tests/temp/category-overpass-api.zip

### MapCSS _____________________________________________________________________

# @see https://wiki.openstreetmap.org/wiki/Category:MapCSS
curl --silent 'https://wiki.openstreetmap.org/w/api.php?action=query&cmtitle=Category:MapCSS&list=categorymembers&format=json' | jq '.query.categorymembers | .[] | .pageid' | tr -s "\n" "|"
# 39064|108476|60558|37578|52585|65349|63929|77220|57712|59754|

wiki_as_base --input-autodetect '39064|108476|60558|37578|52585|65349|63929|77220|57712|59754' --output-zip-file ./tests/temp/category-mapcss.zip


### Category:External_reference_tag ____________________________________________
curl --silent 'https://wiki.openstreetmap.org/w/api.php?action=query&cmtitle=Category:External_reference_tag&list=categorymembers&format=json&formatversion=2' | jq '.query.categorymembers | .[] | .pageid' | tr -s "\n" "|"
# 141977|28801|67580|190684|53003|184981|254895|95210|124074|138320

wiki_as_base --input-autodetect '141977|28801|67580|190684|53003|184981|254895|95210|124074|138320' --output-zip-file ./tests/temp/category-External_reference_tag.zip



### new version of wiki_as_base

wiki_as_base --input-autodetect 'Category:External_reference_tag'
wiki_as_base --input-autodetect 'Category:External_reference_tag' --output-zip-file ./tests/temp/category-External_reference_tag.zip