import subprocess
import time
import pytest


@pytest.fixture(scope="session", autouse=True)
def docker_compose(request):
    """ Run docker-compose """
    print("building docker images and starting containers")
    buildbase = subprocess.Popen(['docker', 'build', '-t',
                                  'simcity-webservice-base', '.'])
    buildbase.wait()
    assert 0 == buildbase.returncode

    compose = subprocess.Popen(['docker-compose', 'up', '--build', '-d'],
                               cwd='integration_tests/docker')
    compose.wait()
    assert 0 == compose.returncode
    time.sleep(10)

    yield

    if request.node.session.testsfailed > 0:
        print("docker logs")
        subprocess.Popen(['docker-compose', 'logs'],
                         cwd='integration_tests/docker').wait()

    print("Stopping docker containers")
    subprocess.Popen(['docker-compose', 'stop'],
                     cwd='integration_tests/docker').wait()

    subprocess.Popen(['docker-compose', 'rm', '-f'],
                     cwd='integration_tests/docker').wait()

    subprocess.Popen(['docker', 'rmi', '-f', 'simcity-webservice-base']).wait()

    assert request.node.session.testsfailed == 0
