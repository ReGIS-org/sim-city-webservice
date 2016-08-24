#!/usr/bin/env python

from distutils.core import setup

setup(name='simcityweb',
      version='0.1',
      description='Python SIM-CITY web service.',
      author='Joris Borgdorff',
      author_email='j.borgdorff@esciencecenter.nl',
      url='https://esciencecenter.nl/projects/sim-city/',
      packages=['simcityweb'],
      install_requires=["gevent", "simcity[xenon]>=0.4", "bottle", "accept-types"],
      extras_require={
          'test': ['pytest', 'pytest-flake8'],
      },
      dependency_links = ['http://github.com/indodutch/sim-city-client/tarball/develop#egg=simcity-0.4'],
      )
