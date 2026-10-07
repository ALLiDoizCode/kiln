"""The kiln command:  python3 -m kiln <command> [arguments]

    run       start an asset from a model file, as far as the shape review
    review    approve or reject an asset's shape review; approving builds it
    rebuild   rebuild assets from their kept raw outputs
    measure   measure one model file

`python3 -m kiln <command> --help` lists a command's arguments.
"""
import sys

from kiln import measure, rebuild, run

COMMANDS = {"run": run.main, "review": run.review_main, "rebuild": rebuild.main, "measure": measure.main}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if argv else 2
    command = COMMANDS.get(argv[0])
    if command is None:
        print(f"kiln: there is no command '{argv[0]}'. Commands: {', '.join(COMMANDS)}",
              file=sys.stderr)
        return 2
    return command(argv[1:])


if __name__ == "__main__":
    sys.exit(main())
