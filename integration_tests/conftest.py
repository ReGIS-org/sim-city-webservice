import subprocess
import time
import pytest

all_tests_passed = True


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    global all_tests_passed
    # execute all other hooks to obtain the report object
    outcome = yield
    all_tests_passed &= not outcome.get_result().failed


@pytest.fixture(scope="module", autouse=True)
def docker_compose():
    global all_tests_passed
    print("building docker images and starting containers")
    compose = subprocess.Popen(['docker-compose', 'up', '--build', '-d'],
                               cwd='integration_tests/docker')
    compose.wait()
    assert 0 == compose.returncode
    time.sleep(10)
    yield

    if not all_tests_passed:
        print("docker logs")
        subprocess.Popen(['docker-compose', 'logs'],
                         cwd='integration_tests/docker').wait()

    print("Stopping docker containers")
    subprocess.Popen(['docker-compose', 'stop'],
                     cwd='integration_tests/docker').wait()

    subprocess.Popen(['docker-compose', 'rm', '-f'],
                     cwd='integration_tests/docker').wait()

    assert all_tests_passed
