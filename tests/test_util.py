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
                             get_minified_filename, get_simulation_version)
from bottle import HTTPResponse
from nose.tools import (assert_equals, assert_raises, assert_not_equal)
import tempfile
import os


def test_make_hash():
    for i in range(10):
        assert_not_equal(make_hash(i), make_hash(i + 1))
        assert_equals(make_hash(i), make_hash(i + 1 - 1))

    for a in "my str":
        assert_not_equal(make_hash(i), make_hash(1))
        assert_equals(make_hash(a), make_hash(chr(ord(a))))


def test_error():
    err = error(400, "message")
    assert_equals(HTTPResponse, type(err))
    assert_equals(400, err.status_code)


def test_abort():
    assert_raises(HTTPResponse, abort, 400, "message")


def test_minified_filename():
    fd, path = tempfile.mkstemp(suffix='.json')
    try:
        # if minified does not exist, return full file
        filedir, filename = os.path.split(path)
        base = filename[:-5]
        assert_equals(filename, get_minified_filename(filedir, base))

        # otherwise, return minified
        minfilename = base + '.min.json'
        with open(os.path.join(filedir, minfilename), 'w'):
            pass
        try:
            assert_equals(minfilename, get_minified_filename(filedir, base))
        finally:
            os.remove(os.path.join(filedir, minfilename))
    finally:
        os.remove(path)


def test_minified_non_exist():
    assert_raises(IOError, get_minified_filename, "dir", "does not exist")


def test_get_simulation_version():
    spec = {
        'latest': 'stable',
        'stable': '1.0',
        '1.0': {},
        'invalid': '2.0',
    }
    assert_equals('1.0', get_simulation_version(spec, '1.0'))
    assert_equals('1.0', get_simulation_version(spec, 'stable'))
    assert_raises(KeyError, get_simulation_version, spec, 'no_exist')
    assert_raises(ValueError, get_simulation_version, spec, 'latest')
    assert_raises(ValueError, get_simulation_version, spec, 'invalid')


def test_get_simulation_config():
    fd, path = tempfile.mkstemp(suffix='.json')
    filedir, filename = os.path.split(path)
    base = filename[:-5]
    spec = '{"latest": "1.0", "1.0": {}, "invalid": "2.0"}'
    with os.fdopen(fd, 'w') as f:
        f.write(spec)

    assert_equals('1.0', get_simulation_config(base, '1.0', filedir)[1])
    assert_equals('1.0', get_simulation_config(base, 'latest', filedir)[1])
    assert_raises(HTTPResponse, get_simulation_config,
                  'non_exist_sim', 'latest', filedir)
    assert_raises(HTTPResponse, get_simulation_config,
                  'base', 'invalid', filedir)
