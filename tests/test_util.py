# SIM-CITY webservice
#
# Copyright 2015 Netherlands eScience Center
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

from simcityweb.util import (make_hash, error, abort, get_simulation_config,
                             get_minified_json, get_simulation_version)
from bottle import HTTPResponse
from pytest import raises
import os


def test_make_hash():
    for i in range(10):
        assert make_hash(i) != make_hash(i + 1)
        assert make_hash(i) == make_hash(i + 1 - 1)

    for a in "my str":
        assert make_hash(i) != make_hash(1)
        assert make_hash(a) == make_hash(chr(ord(a)))


def test_error():
    err = error(400, "message")
    assert HTTPResponse == type(err)
    assert 400 == err.status_code


def test_abort():
    with raises(HTTPResponse):
        abort(400, "message")


def test_minified_filename(tmpdir):
    f = tmpdir.join('test.json')
    f.write('{"a": 2}')

    # if minified does not exist, return full file
    minfilename = 'test.min.json'
    minpath = os.path.join(f.dirname, minfilename)

    assert {'a': 2} == get_minified_json(f.dirname, 'test')

    assert os.path.exists(minpath)
    assert os.stat(minpath).st_size == f.size() - 1


def test_minified_non_exist(tmpdir):
    f = tmpdir.join("does_not_exist")
    try:
        minified_error = FileNotFoundError
    except NameError:
        minified_error = IOError

    with raises(minified_error):
        get_minified_json(str(f), "does not exist")


def test_get_simulation_version():
    spec = {
        'latest': 'stable',
        'stable': '1.0',
        '1.0': {},
        'invalid': '2.0',
    }
    assert '1.0' == get_simulation_version(spec, '1.0')
    assert '1.0' == get_simulation_version(spec, 'stable')
    raises(KeyError, get_simulation_version, spec, 'no_exist')
    raises(ValueError, get_simulation_version, spec, 'latest')
    raises(ValueError, get_simulation_version, spec, 'invalid')


def test_get_simulation_config(tmpdir):
    spec = '{"latest": "1.0", "1.0": {}, "invalid": "2.0"}'
    f = tmpdir.join('test.json')
    f.write(spec)

    assert '1.0' == get_simulation_config('test', '1.0', f.dirname)[1]
    assert '1.0' == get_simulation_config('test', 'latest', f.dirname)[1]
    raises(HTTPResponse, get_simulation_config, 'non_exist_sim', 'latest',
           f.dirname)
    raises(HTTPResponse, get_simulation_config, 'base', 'invalid', f.dirname)
