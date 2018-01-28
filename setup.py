#!/usr/bin/env python3
from setuptools import find_packages, setup
from sweetpotato.common import (AUTHOR_EMAIL, AUTHOR_NAME, DESCRIPTION,
                                LICENSE, PROGNAME, VERSION)


URL = 'http://hristoast.github.io/{}/'.format(PROGNAME)

with open('README.md', 'r') as r:
    rl = r.read()
    r.close()

setup(
    name=PROGNAME,
    version=VERSION,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR_NAME,
    maintainer_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=str(r),
    download_url=URL,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output',
        'Environment :: Web Environment',
        'Framework :: Bottle',
        'License :: OSI Approved :: GNU General Public License v3 or later'
        '(GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Operating System Kernels :: Linux',
        'Topic :: Utilities'],
    platforms=['linux2'],
    license=LICENSE,
    packages=find_packages(),
    entry_points={'console_scripts':
                  ['{0} = {0}.cli:parse_args'.format(PROGNAME), ]})
