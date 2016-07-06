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

from bottle import HTTPResponse
import os
import json
from pkg_resources import parse_version

try:
    FileNotFound = FileNotFoundError
except NameError:
    FileNotFound = IOError


def make_hash(*args):
    value = 0x345678
    for arg in args:
        value = (1000003 * value) ^ hash(arg)
    if value == -1:
        value = -2
    return value


def error(status, message):
    return HTTPResponse({'error': message}, status)


def abort(status, message):
    raise error(status, message)


def get_minified_json(path, name):
    try:
        with open(os.path.join(path, name + '.min.json')) as f:
            return json.load(f)
    except FileNotFound:
        with open(os.path.join(path, name + '.json')) as f:
            data = json.load(f)

        try:
            with open(os.path.join(path, name + '.min.json'), 'w') as f:
                json.dump(data, f, separators=(',', ':'))
        except IOError:
            print('WARNING: cannot write minified json file {0}/{1}.min.json'
                  .format(path, name))

        return data


# Error checking
def get_simulation_config(name, version, path):
    sim = get_json(name, path, 'simulation')
    try:
        version = get_simulation_version(sim, version)
    except KeyError:
        abort(404, 'version "{0}" of simulation "{1}" not found'
              .format(version, name))
    except ValueError:
        abort(500, ('simulation "{0}" is not fully configured on the server; '
                    'contact the server administrator.').format(name))
    return sim, version


def get_json(name, path, json_type):
    if '/' in name or '\\' in name:
        abort(400, json_type + ' name is malformed')

    try:
        return get_minified_json(path, name)
    except FileNotFound:
        abort(404, '{1} "{0}" not found'.format(name, json_type))
    except IOError:
        abort(500, 'failed to read {1} "{0}"'.format(name, json_type))
    except ValueError:
        abort(500, ('{1} "{0}" is not well configured on the server; contact '
                    'the server administrator.').format(name, json_type))


def get_simulation_version(sim_specs, target_version):
    if target_version is None:
        target_version = 'latest'

    if not isinstance(sim_specs[target_version], dict):
        target_version = sim_specs[target_version]

    if (target_version not in sim_specs or
            not isinstance(sim_specs[target_version], dict)):
        raise ValueError

    return target_version


def get_simulation_versions(name):
    sim = get_simulation_config(name, None, 'simulations')[0]
    sorted_versions = sorted([parse_version(v) for v in sim.keys()])
    return [str(version) for version in sorted_versions]
