import argparse
import json
import os
import sys
import wiki_as_base

# from wiki_as_base.wiki_as_base import WikiAsBase2Zip

EXIT_OK = 0  # pylint: disable=invalid-name
EXIT_ERROR = 1  # pylint: disable=invalid-name
EXIT_SYNTAX = 2  # pylint: disable=invalid-name


# Local install of cli (without upload).
#   python3 -m build
#   python3 -m pip install dist/wiki_as_base-0.2.1-py3-none-any.whl --force

# Examples
#   wiki_as_base --page-title 'User:EmericusPetro/sandbox/Wiki-as-base' | jq .data[1].data_raw
#   wiki_as_base --input-stdin < tests/data/multiple.wiki.txt | jq .data[1].data_raw
#   cat tests/data/multiple.wiki.txt | wiki_as_base --input-stdin | jq .data[1].data_raw


def main():

    parser = argparse.ArgumentParser(
        prog="wiki_as_base",
        description="Use MediaWiki Wiki page content as read-only database",
    )

    # parser.add_argument(
    #     'integers', metavar='N', type=int, nargs='+',
    #     help='an integer for the accumulator')
    # parser.add_argument(
    #     '-greet', action='store_const', const=True,
    #     default=False, dest='greet',
    #     help="Greet Message from Geeks For Geeks.")
    # parser.add_argument(
    #     '--sum', dest='accumulate', action='store_const',
    #     const=sum, default=max,
    #     help='sum the integers (default: find the max)')

    # added --titles as aliases existing --page-title
    # parser.add_argument("--page-title", help="Page title of input")
    parser.add_argument(
        "--titles", "--page-title", help="Page titles of input, Use | as separator"
    )

    parser.add_argument("--pageids", help="Pageids of input, Use | as separator")

    parser.add_argument("--revids", help="Revision IDs of input, Use | as separator")

    parser.add_argument(
        "--input-autodetect",
        # action="store_true",
        help="Page titles or pageids (not both). "
        "Syntax sugar for --titles or --pageids. "
        "Use | as separator",
    )

    parser.add_argument(
        "--input-stdin",
        action="store_true",
        help="Use STDIN (data piped from other tools)" "instead of remote API",
    )

    parser.add_argument(
        "--output-raw",
        action="store_true",
        help="Output RAW, unedited Wiki markup (or API response if remote call)",
    )

    # parser.add_argument(
    #     "--output-dir",
    #     help="Output inferred files to a directory. "
    #     "With --verbose will save input text and JSON-LD metadata",
    # )

    parser.add_argument(
        "--output-zip-stdout",
        action="store_true",
        help="Output inferred files to a zip (stdout)"
        "With --verbose will save input text and JSON-LD metadata",
    )

    parser.add_argument(
        "--output-zip-file",
        # action="store_true",
        help="Output inferred files to a zip (file)"
        "With --verbose will save input text and JSON-LD metadata",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")

    args = parser.parse_args()

    # print(args)

    wikitext = None
    # wikiapi_meta = None

    # meta = {}

    args.page_title = args.titles
    # print(args.page_title)

    if (
        not args.page_title
        and not args.pageids
        and not args.revids
        and not args.input_autodetect
        and not args.input_stdin
    ):
        print(
            "Missing --titles, --pagesid, --revids, "
            "or --input-autodetect, or --input-stdin"
        )
        return EXIT_ERROR

    if args.input_stdin:
        wikitext = sys.stdin.read()
        wtdata = wiki_as_base.WikitextAsData().set_wikitext(wikitext)
    elif args.input_autodetect:
        wtdata = wiki_as_base.WikitextAsData().set_pages_autodetect(
            args.input_autodetect
        )
    elif args.page_title:
        wtdata = wiki_as_base.WikitextAsData().set_titles(args.page_title)
    elif args.pageids:
        wtdata = wiki_as_base.WikitextAsData().set_pageids(args.pageids)
    elif args.revids:
        wtdata = wiki_as_base.WikitextAsData().set_revids(args.revids)

    wtdata.prepare()

    if args.output_raw:
        # If multiple pages, behavior may be undefined
        # @TODO use wtdata.is_success()

        api_response = wtdata.get("api_response", strict=False)
        errors = wtdata.get("errors", strict=False)
        if api_response:
            print(json.dumps(api_response, ensure_ascii=False, indent=2))
        elif errors:
            print({"error": errors})
        else:
            print(wtdata.get("wikitext"))

        return EXIT_OK if wtdata.is_success() else EXIT_ERROR

    elif args.output_zip_file:
        # result = wtdata.output_zip(args.output_zip_file)
        wtdata.output_zip(args.output_zip_file)
        return EXIT_OK if wtdata.is_success() else EXIT_ERROR
        # if result:
        #     return EXIT_OK
        # else:
        #     return EXIT_ERROR
    else:
        print(json.dumps(wtdata.output_jsonld(), ensure_ascii=False, indent=2))
        return EXIT_OK if wtdata.is_success() else EXIT_ERROR
        # return EXIT_OK

    # return EXIT_ERROR


if __name__ == "__main__":
    main()


def exec_from_console_scripts():
    main()
