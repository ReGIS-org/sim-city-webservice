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

# Error checking


def get_simulation_config(name, version, config_sim):
    if '/' in name or '\\' in name:
        abort(400, 'simulation name is malformed')

    path = os.path.join(config_sim['path'], name + ".json")
    try:
        with open(path) as f:
            sim_str = f.read()
    except:
        abort(404, 'simulation "' + name + '" not found')

    try:
        sim = json.loads(sim_str)
    except:
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
