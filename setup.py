#!/usr/bin/env python3

from setuptools import setup


setup(
    name='goodline-iptv',
    version='0.1.0',
    description='Goodline EPG and playlist downloader and converter',
    author='SNS',
    author_email='drochu@obeimi.info',
    url='http://www.obeimi.info',
    packages=[],
    include_package_data=True,
    scripts=['load_goodline_iptv.py'],
    install_requires=[
    ],
)
