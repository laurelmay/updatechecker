#!/usr/bin/env python3
import asyncio
import sys

import aiohttp

from updatechecker.checkers import all_checkers

async def main():
    headers = {"User-Agent": "Update Checker Test"}
    checkers = all_checkers()
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        checkers = [checker(session, False) for _, checker in checkers.items()]
        for result in await asyncio.gather(*[checker.load() for checker in checkers], return_exceptions=True):
            print(type(result), result)


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
