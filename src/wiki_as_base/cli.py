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

    parser_input = parser.add_argument_group(
        "input", "Input data. Select ONE of these options"
    )

    parser_input.add_argument(
        "--titles",
        "--page-title",
        help="MediaWiki page titles of input, Use | as separator",
    )

    parser_input.add_argument(
        "--pageids", help="MediaWiki pageids of input, Use | as separator"
    )

    parser_input.add_argument(
        "--revids", help="MediaWiki revision IDs of input, Use | as separator"
    )

    # Not fully implemented. Hidden at the moment
    # parser_input.add_argument(
    #     "--wikibase-ids",
    #     help="(Early draft) WikiBase Q items or P properties. Use | as separator",
    # )

    parser_input.add_argument(
        "--input-autodetect",
        # action="store_true",
        help="Page titles, pageids (not both). "
        "Syntax sugar for --titles or --pageids. "
        "Use | as separator. (experimental) by category content fetch",
    )

    parser_input.add_argument(
        "--input-stdin",
        action="store_true",
        help="Use STDIN (data piped from other tools) instead of remote API",
    )

    parser_output = parser.add_argument_group(
        "output",
        "Output data. Optional. Any of the following options will override the default JSON-LD to stdout option.",
    )

    parser_output.add_argument(
        "--output-streaming",
        action="store_true",
        help="Output JSON Text Sequences (RFC 7464 application/json-seq)",
    )

    # parser.add_argument(
    #     "--output-dir",
    #     help="Output inferred files to a directory. "
    #     "With --verbose will save input text and JSON-LD metadata",
    # )

    parser_output.add_argument(
        "--output-zip-stdout",
        action="store_true",
        help="Output inferred files to a zip (stdout)"
        "With --verbose will save input text and JSON-LD metadata",
    )

    parser_output.add_argument(
        "--output-zip-file",
        # action="store_true",
        help="Output inferred files to a zip (file)"
        "With --verbose will save input text and JSON-LD metadata",
    )

    parser_output.add_argument(
        "--output-file-by-name",
        dest="out_file_stdout",
        help="Filename hint for a single file be printed to stdout",
    )

    parser_output.add_argument(
        "--output-file-by-content",
        dest="out_filestr_stdout",
        help="(NOT IMPLEMNTED YET) Text content hint for a single file to be printed to stdout",
    )

    parser_output.add_argument(
        "--output-raw",
        action="store_true",
        help="[DEBUG] Output RAW, unedited Wiki markup (or API response if remote call)",
    )

    # parser_filter = parser.add_argument_group('filter2', 'Output data. Optional. Any of the following options will override the default JSON-LD to stdout option.')
    parser_filter = parser.add_argument_group(
        "filter",
        "Filter data. Optional. Allow restrict only a subset of the items.",
    )

    parser_filter.add_argument(
        "--filter-item-type",
        # action="store_true",
        help="(experimental) Filter item @type values on JSON-LD. Python REGEX value",
        default=None,
    )

    parser_filter.add_argument(
        "--filter-item-id",
        # action="store_true",
        help="(experimental, not fully implememted) Filter item @id on JSON-LD. Python REGEX value",
        default=None,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose", dest="verbose"
    )

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
        # and not args.wikibase_ids
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
    # elif args.wikibase_ids:
    #     wtdata = wiki_as_base.WikitextAsData().set_wikibaseids(args.wikibase_ids)

    if args.filter_item_type or args.filter_item_id:
        # filters = {
        #     "item_type": args.filter_item_type,
        #     "item_id": args.filter_item_id,
        # }
        # print(args, filters)
        wtdata.set_filters(item_type=args.filter_item_type, item_id=args.filter_item_id)

    if args.verbose:
        wtdata.set_verbose()

    # print(args, filters)

    # sys.exit()
    wtdata.prepare()

    if args.out_file_stdout:
        (
            file_mached,
            list_fileids,
            list_named,
            list_ambiguous,
        ) = wtdata.get_singlefile(args.out_file_stdout)
        if not file_mached:
            print(f"# ERROR: file hint <[{args.out_file_stdout}]> not found")
            print(
                f"#        list_fileids ({len(list_fileids)}) <[{', '.join(list_fileids)}]>"
            )
            print(
                f"#        list_named ({len(list_named)}) <[{', '.join(list_named)}]>"
            )
            print(
                f"#        list_ambiguous ({len(list_ambiguous)}) <[{', '.join(list_ambiguous)}]>"
            )
            return EXIT_ERROR
        else:
            print(file_mached)
            return EXIT_OK

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

    elif args.output_streaming:
        # @TODO maybe hint about errors? But JSON-SEQ allow individual items fail
        #       if malformated, but we could have a full error at input data
        wtdata.output_jsonseq()
        # print("TODO")

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
