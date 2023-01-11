# @TODO add other common formats on <syntaxhighlight lang="">
#       see https://pygments.org/docs/formatters/
#       see https://pygments.org/docs/lexers/
#           - Stopped on 'Lexers for .net languages'; needs check others
import os


_default_langs = {
    "bash": "sh",
    "c": "c",  # what about .h?
    "css": "css",
    "c\+\+": "cpp",
    "cpp": "cpp",
    "dpatch": "dpatch",
    "diff": "diff",
    "udiff": "diff",
    "html": "html",
    "latex": "tex",
    "tex": "tex",
    "json": "json",
    "python": "py",
    # "raw": "raw",
    # "tokens": "raw",
    "sparql": "rq",
    "sql": "sql",
    "svg": "svg",
    "text": "txt",
    "turtle": "ttl",
    "toml": "toml",
    "terraform": "tf",
    "tf": "tf",
    "xml": "xml",
    "yaml": "yml",
}

# WIKI_DATA_LANGS = os.getenv("WIKI_DATA_LANGS", "yaml\nturtle\ntext\ncpp\nsparql\nsql")
WIKI_DATA_LANGS = os.getenv("WIKI_DATA_LANGS", "\n".join(_default_langs.keys()))

# TODO make this configurable per wiki
_default_templates = {
    # https://wiki.openstreetmap.org/wiki/Template:Description
    "Description": "",
    "Feature": "",
    "KeyDescription": "",
    "ValueDescription": "",
    "KeyPrefixDescription": "",
    # https://wiki.openstreetmap.org/wiki/Template:RelationDescription
    "RelationDescription": "",
    # https://wiki.openstreetmap.org/wiki/Template:ElementUsage
    "ElementUsage": "",
}

_WIKI_TEMPLATES = os.getenv("WIKI_TEMPLATES", "\n".join(_default_templates.keys()))
WIKI_TEMPLATES = _WIKI_TEMPLATES.split('\n')
