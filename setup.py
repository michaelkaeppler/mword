# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 21:32:47 2017

@author: Mael
"""
from setuptools import setup

setup(name='mword',
      version='0.1',
      description='Parse a text file and find words that can be expressed with musical note names',
      url='https://github.com/michaelkaeppler/mword',
      author='Michael Kaeppler',
      author_email='xmichael-k@web.de',
      license='GNU GPLv3',
      packages=['mword'],
      install_requires=['argparse', 'multiprocessing', 'logging', 'tqdm'],
      zip_safe=False)