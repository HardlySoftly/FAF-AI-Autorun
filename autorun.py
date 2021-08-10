import argparse
import logging
import sys

from _autorun.batch import run_batch
from _autorun.install import install, uninstall


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True, title="subcommands", metavar="[command]")

    def add_common(parser):
        parser.add_argument("--verbose", "-v", help="Verbosity level", action="count", default=0)
        parser.add_argument("--yes", "-y", help="Answer 'yes' to all prompts", action="store_true")

    # Install
    parser_prep = sub.add_parser("install", help="Install the Autorun Forged Alliance mod")
    parser_prep.set_defaults(func=install)
    add_common(parser_prep)

    # Uninstall
    parser_remove = sub.add_parser("uninstall", help="Remove the installed Autorun files")
    parser_remove.add_argument("--prompt", "-p", help="Prompt before removing files", action="store_true")
    parser_remove.set_defaults(func=uninstall)
    add_common(parser_remove)

    # Batch
    parser_batch = sub.add_parser("batch", help="Run a batch of games")
    parser_batch.add_argument("--num-threads", "-n", help="Number of games to run concurrently", type=int)
    parser_batch.add_argument("--max-game-time", "-t", help="Maximum amount of time to let a game run before declaring it a draw", type=float, default=45 * 60)
    parser_batch.add_argument("--obnoxious", "-o", help="Don't minimize Forged Alliance windows", action="store_true")
    parser_batch.add_argument("--delete-logs", "-d", help="Delete log files after experiments have finished", action="store_true")
    parser_batch.add_argument("--save-results", "-s", help="Write results to a text file instead of printing them", action="store_true")
    parser_batch.add_argument("--dry-run", "-z", help="Dry run only, don't run the games", action="store_true")
    parser_batch.add_argument("--use-affinity", "-a", help="Set process affinity to utilise cores better.  Caps instances at 1 per core, and leaves core 0 free.", action="store_true")
    parser_batch.set_defaults(func=run_batch)
    add_common(parser_batch)

    add_common(parser)

    args = parser.parse_args()

    log = logging.getLogger()
    log.setLevel({
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(args.verbose, 0))
    log.addHandler(logging.StreamHandler(sys.stdout))

    try:
        args.func(args)
    except Exception as e:
        log.warning(f"{e.__class__.__name__}: {e}", exc_info=args.verbose > 0)
