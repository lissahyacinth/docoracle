"""Document Oracle

Usage:
  docoracle <base_dir>
  docoracle (-h | --help)
  docoracle --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import docoracle
from docopt import docopt


if __name__ == "__main__":
    arguments = docopt(__doc__, version=docoracle.__version__)
    print(arguments)
