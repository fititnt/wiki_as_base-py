# How to run
# This will just print the output
#    python ./examples/simple-example-yaml.py
#
# This will use yq (https://mikefarah.gitbook.io/yq/) tool to
# pretty print the output
#    python ./examples/simple-example-yaml.py | yq --yaml-output

import wiki_as_base

wikitext = """
==== Another non example ====
<syntaxhighlight lang="yaml">
- ignore
- this
- list
</syntaxhighlight>

==== Another example ====
<syntaxhighlight lang="yaml">
# Comment
___wikiasbase: true
data:
  test_string: test2
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
    wikitext, 'yaml', has_text='___wikiasbase'
)
# results =
# [('# Comment\n___wikiasbase: true\ndata:\n  test_string: test2', 'yaml')]

if results is not None:
    print(results[0][0])
