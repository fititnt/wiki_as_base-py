import argparse
import json
import wiki_as_base

EXIT_OK = 0  # pylint: disable=invalid-name
EXIT_ERROR = 1  # pylint: disable=invalid-name
EXIT_SYNTAX = 2  # pylint: disable=invalid-name


def main():

    parser = argparse.ArgumentParser(
        prog='wiki_as_base',
        description='Use MediaWiki Wiki page content as read-only database')

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

    parser.add_argument('--page-title')

    args = parser.parse_args()

    # print(args)

    if args.page_title:
        # print("Welcome to GeeksforGeeks !")
        # print(args.page_title)
        result = wiki_as_base.wiki_as_base_request(args.page_title)

        if result:
            data = wiki_as_base.wiki_as_base_all(result)
            if data:
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return EXIT_OK
            else:
                print('{"error": "no data from request"}')
        else:
            print('{"error": "no result from request"}')
            # return EXIT_ERROR
            # print(data)
    #     if args.accumulate == max:
    #         print("The Computation Done is Maximum")
    #     else:
    #         print("The Computation Done is Summation")
    #     print("And Here's your result:", end=" ")
    else:
        print('--page-title ?')

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
