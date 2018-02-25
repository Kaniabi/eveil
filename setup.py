#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='eveil',
    use_scm_version=True,

    author="Alexandre Andrade",
    author_email='kaniabi@gmail.com',

    url='https://github.com/zerotk/eveil',

    description="",
    long_description="",

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='eve, jupyter, esi, swagger',

    include_package_data=True,
    packages=['eveil'],
    # namespace_packages=[''],
    # entry_points="""
    #     [zops.plugins]
    #     main=zops.anatomy.cli:main
    # """,
    install_requires=[],
    dependency_links=[],
    setup_requires=['setuptools_scm'],
    tests_require=[],
    license="MIT license",
)
