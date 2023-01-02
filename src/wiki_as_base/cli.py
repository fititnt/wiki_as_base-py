import argparse
import json
import os
import sys
import wiki_as_base

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

    parser.add_argument("--page-title", help="Page title of input")
    parser.add_argument(
        "--input-stdin",
        action="store_true",
        help="Use STDIN (data piped from other tools)" "instead of remote API",
    )

    parser.add_argument(
        "--output-raw", action="store_true", help="Output RAW, unedited Wiki markup"
    )

    parser.add_argument(
        "--output-dir",
        help="Output inferred files to a directory. "
        "With --verbose will save input text and JSON-LD metadata",
    )

    parser.add_argument(
        "--output-zip",
        help="Output inferred files to a zip file. "
        "With --verbose will save input text and JSON-LD metadata",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")

    args = parser.parse_args()

    # print(args)

    result = None

    if args.page_title:
        # print("Welcome to GeeksforGeeks !")
        # print(args.page_title)
        result = wiki_as_base.wiki_as_base_request(args.page_title)
    elif args.input_stdin:
        # print("Welcome to GeeksforGeeks !")
        # print(args.page_title)
        result = sys.stdin.read()

        # return EXIT_ERROR
        # print(data)
    #     if args.accumulate == max:
    #         print("The Computation Done is Maximum")
    #     else:
    #         print("The Computation Done is Summation")
    #     print("And Here's your result:", end=" ")
    else:
        print("--page-title ?")
        print("--input-stdin ?")
        return EXIT_ERROR

    if args.output_dir and (
        not os.path.exists(args.output_dir) or not os.path.isdir(args.output_dir)
    ):
        raise SyntaxError(f"--output-dir error [{args.output_dir}]")

    if result:

        if args.output_raw:
            print(result)
            return EXIT_OK

        data = wiki_as_base.wiki_as_base_all(result)
        if data:

            print(json.dumps(data, ensure_ascii=False, indent=2))
            return EXIT_OK
        else:
            print('{"error": "no data from request"}')
    else:
        print('{"error": "no result from request"}')

    return EXIT_ERROR

    # print(args.accumulate(args.integers))


if __name__ == "__main__":

    # hxltmcli = HXLTMCLI()
    # pyargs_ = hxltmcli.make_args_hxltmcli()

    # hxltmcli.execute_cli(pyargs_)
    main()


def exec_from_console_scripts():
    # hxltmcli_ = HXLTMCLI()
    # args_ = hxltmcli_.make_args_hxltmcli()

    # hxltmcli_.execute_cli(args_)
    main()
