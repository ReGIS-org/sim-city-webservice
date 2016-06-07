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


def get_minified_filename(path, name, extension='json'):
    if os.path.exists(os.path.join(path, name + '.min.' + extension)):
        return name + '.min.' + extension
    elif os.path.exists(os.path.join(path, name + '.' + extension)):
        return name + '.' + extension

    raise IOError('File {0}/{1}(.min).{2} does not exist'
                  .format(path, name, extension))


# Error checking
def get_simulation_config(name, version, path):
    sim = get_json(name, path)
    try:
        version = get_simulation_version(sim, version)
    except KeyError:
        abort(404, 'version "{0}" of simulation "{1}" not found'
              .format(version, name))
    except ValueError:
        abort(500, ('simulation "{0}" is not fully configured on the server; '
                    'contact the server administrator.').format(name))
    return sim, version


def get_json(name, path):
    if '/' in name or '\\' in name:
        abort(400, 'schema name is malformed')

    try:
        filename = get_minified_filename(path, name)
        with open(os.path.join(path, filename)) as f:
            schema = json.load(f)
    except IOError:
        abort(404, 'schema "{0}" not found'.format(name))
    except ValueError:
        abort(500, ('schema "{0}" is not well configured on the server; '
                    'contact the server administrator.').format(name))
    return schema


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
