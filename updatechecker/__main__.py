#!/usr/bin/env python3

import requests

from updatechecker.checkers import all_checkers

def main():
    session = requests.Session()
    session.headers['User-Agent'] = "Update Checker Test"
    checkers = all_checkers()
    for _, checker in checkers.items():
        check = checker({}, session, False)
        check.load()
        print(check)


if __name__ == '__main__':
    main()