from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='updatechecker',
    version='0.1.0',
    description='Checks for updates for configured projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kylelaker/updatechecker',
    author='Kyle Laker',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.7',
    install_requires=[
        'beautifulsoup4',
        'click',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'test-update=updatechecker.main:main',
        ],
    },
)
