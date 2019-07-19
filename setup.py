#!/usr/bin/env python

import os
from setuptools import setup, find_packages

install_requires = [
    line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "REQUIREMENTS.txt"))
]
print(install_requires)
#dependency_links = ['git+https://github.com/czbiohub/imagingDB.git@add_setup#egg=imagingDB']


setup(name='InSituToolkit',
      install_requires=install_requires,
      version='0.0.1',
      description='Tools for in situ transcriptomics analysis',
      url='https://github.com/czbiohub/InSituToolkit',
      author='Kevin Yamauchi',
      author_email='kevin.yamauchi@czbiohub.org',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)