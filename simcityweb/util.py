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
import yaml
import six
from pkg_resources import parse_version

try:
    FileNotFound = FileNotFoundError
except NameError:
    FileNotFound = IOError


def error(status, message):
    return HTTPResponse({'error': message}, status)


def abort(status, message):
    raise error(status, message)


class Simulation:
    def __init__(self, name, version, description):
        self.name = name
        self.version = version
        if not isinstance(description, dict):
            raise ValueError
        self.description = description


class SimulationConfig:
    def __init__(self, name, path):
        self.simulations = {}
        self.name = name
        self.load_simulations(name, path)

    # Error checking
    def load_simulations(self, name, path):
        sim = get_json(name, path, 'simulation')
        versions = sim.keys()

        aliases = {}
        for version in versions:
            if isinstance(sim[version], six.string_types):
                aliases[version] = sim[version]
            else:
                self.simulations[version] = self.make_simulation(sim, name, version)
        
        for version in aliases:
            self.simulations[version] = self.get_simulation(version, aliases=aliases)

    def get_simulation(self, version, aliases=None):
        target_version = self.get_simulation_version(version, aliases=aliases)

        if target_version not in self.simulations:
            raise KeyError
        if not isinstance(self.simulations[target_version], Simulation):
            raise ValueError

        return self.simulations[target_version]
    
    def make_simulation(self, sim, name, version):
        return Simulation(name, version, sim[version])

    def get_simulation_version(self, target_version, aliases=None):
        """
        Get the actual version of the Simulation
        
        e.g. latest becomes 0.1
        """
        if target_version is None:
            target_version = 'latest'
        
        while aliases is not None and target_version in aliases:
            print("Target version is now: ", target_version)
            target_version = aliases[target_version]

        return target_version
    
    def get_versions(self):
        return sorted(list(self.simulations.keys()))

def get_minified_json(path, name):
    yaml_path = os.path.join(path, name + '.yaml')
    minified_path = os.path.join(path, name + '.min.json')
    if os.path.isfile(minified_path) and \
        (not os.path.isfile(yaml_path)
        or os.path.getmtime(yaml_path) == os.path.getmtime(minified_path)):
       with open(minified_path, 'r') as f:
           return json.load(f)
    else:
        data = minify_and_load_json(path, name)
        return data


def minify_and_load_json(path, name):
    yaml_path = os.path.join(path, name + '.yaml')
    json_path = os.path.join(path, name + '.json')
    minified_path = os.path.join(path, name + '.min.json')
    if os.path.isfile(yaml_path):
        with open(yaml_path) as f:
            data = yaml.load(f)
    elif os.path.isfile(json_path):
        with open(json_path) as f:
            data = json.load(f)
    else:
        raise IOError('Could not open {0} nor {1}'.format(yaml_path, json_path))

    try:
        with open(minified_path, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
    except IOError:
        print('WARNING: cannot write minified json file {0}/{1}.min.json'
            .format(path, name))
    return data


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

def view_to_json(view):
    ret = {
        'total_rows': view.total_rows,
        'rows': view.rows,
        'offset': view.offset,
    }
    if view.update_seq is not None:
        ret['update_seq'] = view.update_seq
    return ret
