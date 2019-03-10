#!/usr/bin/env python3

from setuptools import setup


try:
    with open('BUILD_NUMBER') as f:
        BUILD_NUMBER = int(f.read())
except:
    BUILD_NUMBER = 0


setup(
    name='goodline-iptv',
    version=f'0.2.{BUILD_NUMBER}',
    description='Goodline EPG and playlist downloader and converter',
    author='Nickolay Sadovskiy',
    author_email='sns1081@gmail.com',
    url='https://github.com/nsadovskiy/goodline_tv',
    packages=['goodline_iptv'],
    include_package_data=True,
    scripts=['import_goodline_iptv.py'],
    install_requires=[
        'aiohttp',
        'aiofiles',
        'teamcity-messages'
    ],
)
