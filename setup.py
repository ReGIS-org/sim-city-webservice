#!/usr/bin/env python

from distutils.core import setup

setup(name='simcityweb',
      version='0.1',
      description='Python SIM-CITY web service.',
      author='Joris Borgdorff',
      author_email='j.borgdorff@esciencecenter.nl',
      url='https://esciencecenter.nl/projects/sim-city/',
      packages=['simcityweb'],
      install_requires=["gevent", "simcity", "simcityexplore", "bottle", "couchdb", "picas"],
     )
