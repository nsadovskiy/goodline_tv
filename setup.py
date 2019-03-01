#!/usr/bin/env python3

from setuptools import setup


setup(
    name='goodline-iptv',
    version='0.2.0',
    description='Goodline EPG and playlist downloader and converter',
    author='Nickolay Sadovskiy',
    author_email='sns1081@gmail.com',
    url='https://github.com/nsadovskiy/goodline_tv',
    packages=['goodline_iptv'],
    include_package_data=True,
    scripts=['import_goodline_iptv.py'],
    install_requires=[
        'aiohttp',
        'aiofiles'
    ],
)
