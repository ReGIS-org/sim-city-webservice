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

#
# This file implements a mock version of the normal webservice
#
import bottle
from bottle import (post, get, run, delete, request, response, HTTPResponse,
                    static_file, hook)
from simcity import parse_parameters
from simcity.util import listfiles
from simcityweb.util import get_simulation_versions
from simcityweb import error, get_simulation_config
from uuid import uuid4
import os
import json

prefix = '/explore'

# Get project directory
file_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(file_dir)

config_sim = {'max_jobs': 1}
config_hosts = {}

# Mock database using a dictionary
mock_db = dict()


# Load a json file with pre made test tasks
def load_pre_made_tasks():
    for _root, dirs, files in os.walk('mock_tasks', topdown=False):
        for name in files:
            if name.endswith('.json'):
                filename = os.path.join(_root, name)
                with open(filename) as _file:
                    task = json.load(_file)
                    mock_db[task['id']] = task

# WARNING:
# Loading the json file in this manner probably means
# it is loaded for every request so we shouldn't make too many
load_pre_made_tasks()

# Remove spaces from json output
bottle.uninstall('json')
bottle.install(bottle.JSONPlugin(
    json_dumps=lambda x: json.dumps(x, separators=(',', ':'))))


# Remove trailing / from request
@hook('before_request')
def strip_path():
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')


@get(prefix)
def root():
    return get_doc_type('swagger')


@get(prefix + '/doc')
def get_doc():
    doc_format = request.query.get('format', 'html')
    return get_doc_type(doc_format)


@get(prefix + '/doc')
def get_doc():
    doc_format = request.query.get('format', 'html')
    return get_doc_type(doc_format)


def get_doc_type(doc_type):
    docs = {
        'html': 'apiary.html',
        'swagger': 'swagger.json',
        'api-blueprint': 'apiary.apib'
    }
    if doc_type not in docs:
        return error(409, "documentation {0} not found. choose between {1}"
                     .format(doc_type, docs.keys()))

    return static_file(os.path.join('docs', docs[doc_type]), root=project_dir)


@get(prefix + '/simulate')
def simulate_list():
    simulations = {}
    try:
        for f in listfiles('simulations'):
            if not f.endswith('.json') or f.endswith('.min.json'):
                continue

            name = f[:-5]
            simulations[name] = {
                'name': name,
                'versions': get_simulation_versions(name)
            }

        return simulations
    except HTTPResponse as ex:
        return ex


@get(prefix + '/simulate/<name>')
def get_simulation_by_name(name):
    try:
        response.status = 200
        return {'name': name, 'versions': get_simulation_versions(name)}
    except HTTPResponse as ex:
        return ex


@get(prefix + '/simulate/<name>/<version>')
def get_simulation_by_name_version(name, version=None):
    try:
        sim, version = get_simulation_config(name, version, 'simulations')
        chosen_sim = sim[version]
        chosen_sim['name'] = name
        chosen_sim['version'] = version
        response.status = 200
        return chosen_sim
    except HTTPResponse as ex:
        return ex


@post(prefix + '/simulate/<name>')
def simulate_name(name):
    return simulate_name_version(name)


@post(prefix + '/simulate/<name>/<version>')
def simulate_name_version(name, version=None):
    if not hasattr(simulate_name_version, 'nextId'):
        # Initialize static variable
        simulate_name_version.nextId = 0

    try:
        sim, version = get_simulation_config(name, version, 'simulations')
        sim = sim[version]
        query = dict(request.json)
        if '_id' in query:
            task_id = query['_id']
            del query['_id']
        else:
            task_id = str(simulate_name_version.nextId)
            simulate_name_version.nextId += 1

        parse_parameters(query, sim['properties'])
    except HTTPResponse as ex:
        return ex
    except ValueError as ex:
        return error(400, ex)
    except EnvironmentError as ex:
        return error(500, ex.message)

    # Create the response we would normally get from
    # the database
    task_props = {
        'id': task_id,
        'key': task_id,
        'value': {
            '_id': task_id,
            '_rev': uuid4().hex,
            'lock': 0,
            'done': 0,
            'name': name,
            'command': sim['command'],
            'arguments': sim.get('arguments', []),
            'parallelism': sim.get('parallelism', '*'),
            'version': version,
            'input': query,
            'uploads': {},
            'error': []
        }
    }

    if 'ensemble' in query:
        task_props['ensemble'] = query['ensemble']
    if 'simulation' in query:
        task_props['simulation'] = query['simulation']

    if task_id in mock_db:
        return error(400, "simulation name " + task_id + " already taken")

    # Add the new task to the "database"
    mock_db[task_id] = task_props

    response.status = 201  # created

    # Normally we return a link to the database, but now
    # we point to sim-city-webservice
    host = bottle.request.get_header('host')
    url = '%s/task/%s' % (host, task_id)
    response.set_header('Location', url)
    return task_props


@get(prefix + '/schema')
def schema_list():
    files = listfiles('schemas')
    return {'schemas': [f[:-5] for f in files if f.endswith('.json')]}


@get(prefix + '/schema/<name>')
def schema_name(name):
    return static_file(os.path.join('schemas', name + '.json'),
                       root=project_dir)


@get(prefix + '/resource')
def resource_list():
    files = listfiles('resources')
    return {"resources": [f[:-5] for f in files if f.endswith('.json')]}


@get(prefix + '/resource/<name>')
def resource_name(name):
    return static_file(os.path.join('resources', name + '.json'),
                       root=project_dir)


@get(prefix + '/view/totals')
def overview():
    try:
        return mock_overview_total()
    except:
        return error(500, "cannot read overview")


def mock_overview_total():
    views = ['todo', 'locked', 'error', 'done', 'unknown',
             'finished_jobs', 'active_jobs', 'pending_jobs']

    num = dict((view, 0) for view in views)

    for key, task in mock_db.items():
        val = task['value']
        if val['done'] > 0:
            num['done'] += 1
        elif val['lock'] > 0:
            num['locked'] += 1
        elif val['lock'] == 0:
            num['todo'] += 1
        elif val['lock'] == -1:
            num['error'] += 1
        else:
            num['unknown'] += 1

    return num


@post(prefix + '/job')
def submit_job():
    if not hasattr(submit_job, 'batch_id'):
        submit_job.batch_id = 1

    # Mock the response for submitting the job
    host = config_sim['default_host']
    _prefix = host + '-'
    batch_id = str(submit_job.batch_id)
    submit_job.batch_id += 1
    job_id = 'job_' + _prefix + uuid4().hex

    response.status = 201  # created
    return {'_id': job_id, 'batch_id': batch_id, 'hostname': host}


@get(prefix + '/simulation/<_id>')
def get_simulation(_id):
    if _id in mock_db:
        return mock_db[_id]['value']
    else:
        return error(404, "simulation does not exist")


@get(prefix + '/view/simulations/<name>/<version>')
def simulations_view(name, version):
    ensemble = request.query.get('ensemble')
    version = get_simulation_config(name, version, 'simulations')[1]

    simulations = [task for k, task in mock_db.items() if
                   task['value']['name'] == name and
                   task['value']['version'] == version and
                   (ensemble is None or task['value']['ensemble'] == ensemble)]

    response.status = 200
    return {'total_rows': len(simulations), 'offset': 0, 'rows': simulations}


@get(prefix + '/simulation/<id>/<attachment>')
def get_attachment(id, attachment):
    return static_file(os.path.join('mock_results', attachment), root=project_dir)


@delete(prefix + '/simulation/<_id>')
def del_simulation(_id):
    rev = request.query.get('rev')
    if rev is None:
        rev = request.get_header('If-Match')
    if rev is None:
        return error(409, "revision not specified")

    if _id in mock_db:
        task = mock_db[_id]
        if task['value']['_rev'] == rev:
            del mock_db[_id]
            return {'ok': True}
        else:
            return error(409, "resource conflict")
    else:
        return error(404, "Resource does not exist")


@get(prefix + '/hosts')
def get_hosts():
    return config_hosts

if __name__ == '__main__':
    run(host='localhost', port=9090, server='wsgiref')
