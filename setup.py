#-*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='zerows',
    version='1.0.0',
    description='Websockets built on top of tornado & zeromq',
    long_description=long_description,
    url='https://github.com/sebastianlach/zerows',
    author='Sebastian Łach',
    author_email='root@slach.eu',
    license='MIT',
    keywords='zerows zero ws zeromq tornado websocket',
    packages=['zerows'],
    install_requires=['tornado'],
    entry_points={
        'console_scripts': [
            'zerows=zerows:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Networking',
        'Operating System :: Unix',
    ],
)
