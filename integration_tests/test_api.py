import requests
from nose.tools import assert_equals, assert_true
import time

host = 'http://localhost:9098/explore'


def make_request(path, status_code, content_type=None, method='GET', base=host,
                 **kwargs):
    response = requests.request(method, base + path, **kwargs)
    if isinstance(status_code, int):
        assert_equals(status_code, response.status_code)
    else:
        assert_true(response.status_code in status_code)
    if content_type is not None:
        assert_true(response.headers['content-type'].lower()
                    .startswith(content_type.lower()),
                    msg='Response content type "{0}" does not match expected '
                        'content type "{1}".'
                    .format(response.headers['content-type'], content_type))
    return response


def test_root():
    make_request('', 200, 'application/json')
    make_request('/', 200, 'application/json')


def test_doc():
    make_request('/doc', 200, 'text/html; charset=utf-8')
    make_request('/doc', 200, 'application/json',
                 headers={'accept': 'application/json'})
    make_request('/doc', 200, 'text/markdown; charset=utf-8',
                 headers={'accept': 'text/markdown'})
    make_request('/doc', 406, headers={'accept': 'text/plain'})
    make_request('/doc', 200, 'text/html; charset=utf-8',
                 headers={'accept': '*/*'})


def test_simulations():
    response = make_request('/simulate', 200, 'application/json')
    obj = response.json()
    assert_true('test_simulation' in obj)
    assert_true('0.1' in obj['test_simulation']['versions'])
    assert_true('0.2' in obj['test_simulation']['versions'])
    assert_true('latest' in obj['test_simulation']['versions'])


def test_simulation():
    response_latest = make_request('/simulate/test_simulation/latest', 200,
                                   'application/json')

    response_0_2 = make_request('/simulate/test_simulation/0.2', 200,
                                'application/json')
    assert_equals(response_latest.content, response_0_2.content)


def test_wrong_simulation():
    make_request('/simulate/noexist', 404)
    make_request('/simulate/test_simulation/noexist', 404)
    make_request('/simulate/noexist', 404, method='POST', json={})
    make_request('/simulate/test_simulation/noexist', 404, method='POST',
                 json={})


def test_submit():
    response = make_request('/simulate/test_simulation/latest', 201,
                            method='POST', json={
                                'command': 'echo',
                                'arg': 'Hello!',
                            })
    assert_true('location' in response.headers)
    simulation_url = response.headers['location']
    response = make_request(simulation_url, 200, 'application/json',
                            base='http://localhost:9098')
    obj = response.json()
    assert_equals('echo', obj['input']['command'])
    time.sleep(3)
    response = make_request(simulation_url, 200, 'application/json',
                            base='http://localhost:9098')
    obj = response.json()
    print(obj)
    response = make_request('/view/totals', 200, 'application/json')
    print(response.json())
    assert_true(obj['lock'] > 0)   
    assert_true(obj['done'] > 0)   
    assert_equals(2, len(obj['files']))
    assert_true('stderr.txt' in obj['files'])
    assert_true('stdout.txt' in obj['files'])
    assert_equals('text/plain', obj['files']['stderr.txt']['content_type'])
    assert_equals(0, obj['files']['stderr.txt']['length'])
    assert_equals('text/plain', obj['files']['stdout.txt']['content_type'])
    assert_equals(len('Hello!\n'), obj['files']['stdout.txt']['length'])
    stdout = make_request('/simulation/{0}/stdout.txt'.format(obj['_id']), 200,
                          'text/plain')
    assert_equals('Hello!\n', stdout.text)


def test_submit_with_params():
    make_request('/simulate/test_simulation/latest', 412, method='POST',
                 params={'command': 'echo', 'arg': 'Hello!'})


def test_submit_double():
    make_request('/simulate/test_simulation/latest', 201, method='POST',
                 json={'_id': 'a', 'command': 'echo', 'arg': 'Hello!'})
    make_request('/simulate/test_simulation/latest', 409, method='POST',
                 json={'_id': 'a', 'command': 'echo', 'arg': 'Hello!'})


def test_submit_missing_parameter():
    make_request('/simulate/test_simulation/latest', 412, method='POST',
                 json={'command': 'echo'})


def test_submit_wrong_parameter():
    make_request('/simulate/test_simulation/latest', 412, method='POST',
                 json={
                    'command': 'tr',
                    'arg': '\n'
                 })
    make_request('/simulate/test_simulation/latest', 412, method='POST',
                 json={
                    'command': 'echo',
                    'arg': 'much too long this argument is'
                 })
