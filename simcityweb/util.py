# SIM-CITY webservice
#
# Copyright 2015 Joris Borgdorff <j.borgdorff@esciencecenter.nl>
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
def get_simulation_config(name, version, config_sim):
    if '/' in name or '\\' in name:
        abort(400, 'simulation name is malformed')

    try:
        filename = get_minified_filename(config_sim['path'], name)
        with open(os.path.join(config_sim['path'], filename)) as f:
            sim = json.load(f)
    except IOError:
        abort(404, 'simulation "' + name + '" not found')
    except ValueError:
        abort(500, 'simulation "' + name +
                   '" is not well configured on the server; ' +
                   'contact the server administrator.')

    if version is None:
        version = 'latest'

    if version not in sim:
        abort(404, 'version "' + version +
              '" of simulation "' + name + '" not found')

    try:
        while type(sim[version]) != dict:
            version = sim[version]
    except KeyError:
        abort(500, 'simulation "' + name +
              '" is not fully configured on the server; ' +
              'contact the server administrator.')

    return (sim, version)
