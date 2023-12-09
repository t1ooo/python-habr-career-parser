from habr_career_parser import save
from habr_career_parser.args import parse_args
from habr_career_parser.rss_parser import RssParser
import sys
import logging

logging.basicConfig(level=logging.INFO)


def main(args: list[str]):
    pargs = parse_args(args)

    parse = RssParser(
        sort=pargs.sort,
        remote=pargs.remote,
        skill=pargs.skill,
        employment=pargs.employment,
        query=pargs.query,
        delay=pargs.delay,
    )

    pargs.save = pargs.save or sys.stdout
    save.to_csv(pargs.save, parse.parse(pargs.page))


if __name__ == "__main__":
    main(sys.argv[1:])
