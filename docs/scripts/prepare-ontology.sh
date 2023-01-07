#!/bin/bash
#===============================================================================
#
#          FILE:  prepare-ontology.sh
#
#         USAGE:  ./scripts/prepare-ontology.sh
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - rdfpipe 
#                   - (pip install rdflib)
#                 - riot
#                   - (https://jena.apache.org/)
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Emerson Rocha <rocha[at]ieee.org>
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v1.0
#       CREATED:  2023-01-13 04:45 UTC started.
#      REVISION:  ---
#===============================================================================
set -e
set -x

# __ROOTDIR="$(pwd)"
# ROOTDIR="${ROOTDIR:-$__ROOTDIR}"

# rdfpipe --input-format=turtle --output-format=application/rdf+xml "$ROOTDIR/ns/wikitext-data.ttl"
# rdfpipe --input-format=turtle --output-format=application/rdf+xml "./ns/wikitext-data.ttl"
# riot --validate "./ns/wikitext-data.ttl"

# First, validate or fail
riot --validate "./ns/wikitext-data.ttl"

riot --formatted=rdfxml "./ns/wikitext-data.ttl" > "./ns/wikitext-data.rdf"
riot --formatted=jsonld "./ns/wikitext-data.ttl" > "./ns/wikitext-data.jsonld"

# @TODO only re-generate the NTriples if .rdf changed
# riot --formatted=ntriples "./ns/wikitext-data.ttl" > "./ns/wikitext-data.nt"