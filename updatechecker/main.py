import hashlib
import json
import sys

import click
import requests

from updatechecker.checkers.eclipse_java import EclipseJavaChecker
from updatechecker.checkers.jgrasp import JGraspChecker
from updatechecker.checker import BaseUpdateCheckerEncoder


@click.command('test-update')
@click.option(
    '--beta',
    '-b',
    is_flag=True,
    help="Whether to accept beta flags"
)
def main(beta):
    session = requests.Session()
    context = {
        'eclipse': {
            'mirror_url': 'http://mirror.math.princeton.edu/pub/eclipse/technology/epp/downloads/release',
        },
    }
    eclipse = EclipseJavaChecker(context, session, beta)
    jgrasp = JGraspChecker(context, session, beta)

    print(json.dumps([eclipse, jgrasp], indent=4, cls=BaseUpdateCheckerEncoder))

    return 0


if __name__ == '__main__':
    sys.exit(main())
