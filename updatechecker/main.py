import sys

import requests

from updatechecker.checkers.eclipse_java import EclipseJavaChecker
from updatechecker.checkers.jgrasp import JGraspChecker


def main():
    session = requests.Session()
    context = {
        'eclipse': {
            'mirror_url': 'http://mirror.math.princeton.edu/pub/eclipse/technology/epp/downloads/release',
        },
    }
    eclipse = EclipseJavaChecker(context, session)
    jgrasp = JGraspChecker(context, session)
    print(eclipse.get_latest())
    print(jgrasp.get_latest())
    return 0


if __name__ == '__main__':
    sys.exit(main())
