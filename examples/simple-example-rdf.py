# How to run
# This will just print the output
#    python ./examples/simple-example-rdf.py
#
# This will use rdfpipe (https://github.com/RDFLib/rdflib)
# (pip install rdflib), to manage the output
#    python ./examples/simple-example-rdf.py | rdfpipe -
#    python ./examples/simple-example-rdf.py | rdfpipe --output-format=json-ld -

import wiki_as_base

wikitext = """
==== Another non example ====
<syntaxhighlight lang="yaml">
- ignore
- this
- list
</syntaxhighlight>

==== Another example ====
<syntaxhighlight lang="turtle">
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX osmnode: <https://www.openstreetmap.org/node/>
PREFIX osmrel: <https://www.openstreetmap.org/relation/>
PREFIX osmway: <https://www.openstreetmap.org/way/>
PREFIX osmm: <https://example.org/todo-meta/>
PREFIX osmt: <https://wiki.openstreetmap.org/wiki/Key:>
PREFIX osmx: <https://example.org/todo-xref/>
PREFIX wikidata: <http://www.wikidata.org/entity/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

osmnode:1
    osmm:changeset 124176968 ;
    osmm:loc "Point(42.7957187 13.5690032)"^^geo:wktLiteral ;
    osmm:timestamp "2022-07-28T09:47:39Z"^^xsd:dateTime ;
    osmm:type "n" ;
    osmm:user "owene" ;
    osmm:userid 29598 ;
    osmm:version 33 ;
    osmt:communication:microwave "yes" ;
    osmt:communication:radio "fm" ;
    osmt:description "Radio Subasio" ;
    osmt:frequency "105.5 MHz" ;
    osmt:man_made "mast" ;
    osmt:name "Monte Piselli - San Giacomo" ;
    osmt:tower:construction "lattice" ;
    osmt:tower:type "communication" ;
.
</syntaxhighlight>

==== ValueDescription ====
<syntaxhighlight lang="text">
{{ValueDescription
|key=highway
}}
</syntaxhighlight>
"""

# List of tuples; first value is content, second is lang
results = wiki_as_base.wiki_as_base_from_syntaxhighlight(
    wikitext, 'turtle',
    has_text='PREFIX osmt: <https://wiki.openstreetmap.org/wiki/Key:>'
)

if results is not None:
    print(results[0][0])

## Will print this:
# PREFIX geo: <http://www.opengis.net/ont/geosparql#>
# PREFIX osmnode: <https://www.openstreetmap.org/node/>
# PREFIX osmrel: <https://www.openstreetmap.org/relation/>
# PREFIX osmway: <https://www.openstreetmap.org/way/>
# PREFIX osmm: <https://example.org/todo-meta/>
# PREFIX osmt: <https://wiki.openstreetmap.org/wiki/Key:>
# PREFIX osmx: <https://example.org/todo-xref/>
# PREFIX wikidata: <http://www.wikidata.org/entity/>
# PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# osmnode:1
#     osmm:changeset 124176968 ;
#     osmm:loc "Point(42.7957187 13.5690032)"^^geo:wktLiteral ;
#     osmm:timestamp "2022-07-28T09:47:39Z"^^xsd:dateTime ;
#     osmm:type "n" ;
#     osmm:user "owene" ;
#     osmm:userid 29598 ;
#     osmm:version 33 ;
#     osmt:communication:microwave "yes" ;
#     osmt:communication:radio "fm" ;
#     osmt:description "Radio Subasio" ;
#     osmt:frequency "105.5 MHz" ;
#     osmt:man_made "mast" ;
#     osmt:name "Monte Piselli - San Giacomo" ;
#     osmt:tower:construction "lattice" ;
#     osmt:tower:type "communication" ;
# .
