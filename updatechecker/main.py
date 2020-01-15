import hashlib
import sys

import click
import requests

from updatechecker.checkers.eclipse_java import EclipseJavaChecker
from updatechecker.checkers.jgrasp import JGraspChecker


def _print_info(name, checker, beta):
    url = checker.get_latest(beta)
    print(name)
    if not url:
        print(f'  Unable to determine latest{" beta" if beta else ""} version')
        return
    print(f'   URL: {url}')
    print(f'  SHA1: ', end='', flush=True)
    print(checker.get_sha1_hash())


def _hash_download(url):
    return hashlib.sha1(requests.get(url).content).hexdigest()


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
    eclipse = EclipseJavaChecker(context, session)
    _print_info('Eclipse', eclipse, beta)
    jgrasp = JGraspChecker(context, session)
    _print_info('jGRASP', jgrasp, beta)
    return 0


if __name__ == '__main__':
    sys.exit(main())
