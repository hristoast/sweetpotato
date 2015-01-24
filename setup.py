from setuptools import find_packages, setup


author_email = __import__('sweetpotato').AUTHOR_EMAIL
author_name = __import__('sweetpotato').AUTHOR_NAME
description = __import__('sweetpotato').DESCRIPTION
lic = __import__('sweetpotato').LICENSE
progname = __import__('sweetpotato').PROGNAME
version = __import__('sweetpotato').VERSION
URL = 'http://hristoast.github.io/sweetpotato/'

setup(
    name=progname,
    version=version,
    author=author_name,
    author_email=author_email,
    maintainer=author_name,
    maintainer_email=author_email,
    url=URL,
    description=description,
    # long_description=,  # TODO
    download_url=URL,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output',
        'Environment :: Web Environment',
        'Framework :: Bottle',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
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
    # platforms=,  # TODO
    license=lic,
    data_files=[
        ('', ['README.md']),
        ('data/static', [
            'data/static/gnu-cat.png',
            'data/static/sweetpotato.min.css']),
        ('data/tpl', [
            'data/tpl/404.tpl',
            'data/tpl/500.tpl',
            'data/tpl/backup.tpl',
            'data/tpl/base.tpl',
            'data/tpl/index.tpl',
            'data/tpl/lower_nav.tpl',
            'data/tpl/readme_no_md.tpl',
            'data/tpl/server.tpl'])
    ],
    packages=find_packages(),
    entry_points={'console_scripts': [
        'sweetpotato = sweetpotato:main'
    ]}
)
