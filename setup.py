#!/usr/bin/env python

from distutils.core import setup

simcity_url = ('git+ssh://git@github.com/indodutch/sim-city-client.git'
               '@develop#egg=simcity-0.4')

setup(name='simcityweb',
      version='0.1',
      description='Python SIM-CITY web service.',
      author='Joris Borgdorff',
      author_email='j.borgdorff@esciencecenter.nl',
      url='https://esciencecenter.nl/projects/sim-city/',
      packages=['simcityweb'],
      install_requires=["gevent", "bottle", "accept-types", 'simcity[xenon]'],
      extras_require={
          'test': ['pytest', 'pytest-flake8'],
      },
      dependency_links=[simcity_url],
      )
