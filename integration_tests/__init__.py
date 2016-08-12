import subprocess
import time
from nose.tools import assert_equals


def setup():
    print("building docker images and starting containers")
    compose = subprocess.Popen(['docker-compose', 'up', '--build', '-d'],
                               cwd='integration_tests/docker')
    compose.wait()
    assert_equals(0, compose.returncode)
    time.sleep(10)


def teardown():
    print("Stopping docker containers")
    subprocess.Popen(['docker-compose', 'stop'],
                     cwd='integration_tests/docker').wait()
    subprocess.Popen(['docker-compose', 'rm', '-f'],
                     cwd='integration_tests/docker').wait()
