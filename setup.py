#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='django-contactform',
      version='2.0.4',
      description='django-contactform',
      author='Nephila',
      author_email='info@nephila.it',
      packages=['contactform',],
      include_package_data=True,
     )
