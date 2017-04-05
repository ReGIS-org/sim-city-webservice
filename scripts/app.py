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
import tempfile

from gevent import monkey; monkey.patch_all()  # noqa E702

import bottle
from bottle import (post, get, run, delete, request, response, HTTPResponse,
                    static_file, hook)
import simcity
from simcity.util import listfiles
from simcityweb.util import SimulationConfig, Simulation, view_to_json
from simcityweb import error
from couchdb.http import (ResourceConflict, Unauthorized, ResourceNotFound,
                          PreconditionFailed, ServerError)
import os
import json
import yaml
import accept_types

simcity.init(None)

config_sim = simcity.get_config().section('Simulations')
couch_cfg = simcity.get_config().section('task-db')
prefix = '/explore'

# Get project directory
file_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(file_dir)

# Remove spaces from json output
bottle.uninstall('json')
bottle.install(bottle.JSONPlugin(
    json_dumps=lambda x: json.dumps(x, separators=(',', ':'))))


@hook('before_request')
def strip_path():
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')


@get(prefix)
def root():
    doc_dir = os.path.join(project_dir, 'docs')
    return static_file('swagger.json', mimetype='application/json',
                       root=doc_dir)


@get(prefix + '/doc')
def get_doc():
    docs = [
        ('text/html', 'apiary.html'),
        ('application/json', 'swagger.json'),
        ('text/markdown', 'apiary.apib'),
    ]
    accept = accept_types.get_best_match(
        request.headers.get('Accept'), [t[0] for t in docs])

    if accept is None:
        return error(406, "documentation {0} not found. choose between {1}"
                     .format(accept, [t[0] for t in docs]))

    doc_dir = os.path.join(project_dir, 'docs')
    return static_file(dict(docs)[accept], mimetype=accept, root=doc_dir)


@get(prefix + '/simulate')
def simulate_list():
    simulations = {}
    try:
        for f in listfiles('simulations'):
            if not (f.endswith('.yaml') or f.endswith('.json'))
               or f.endswith('.min.json'):
                continue

            name = f[:-5]
            config = SimulationConfig(name, 'simulations')
            simulations[name] = {
                'name': name,
                'versions': config.get_versions()
            }

        return simulations
    except HTTPResponse as ex:
        return ex


@get(prefix + '/simulate/<name>')
def get_simulation_by_name(name):
    try:
        config = SimulationConfig(name, 'simulations')
        return {'name': name, 'versions': config.get_versions()}
    except HTTPResponse as ex:
        return ex


@get(prefix + '/simulate/<name>/<version>')
def get_simulation_by_name_version(name, version=None):
    try:
        config = SimulationConfig(name, 'simulations')
        sim = config.get_simulation(version)
        chosen_sim = sim.description
        chosen_sim['name'] = sim.name
        chosen_sim['version'] = sim.version
        return chosen_sim
    except HTTPResponse as ex:
        return ex


@post(prefix + '/simulate/<name>')
def simulate_name(name):
    return simulate_name_version(name)


@post(prefix + '/simulate/<name>/<version>')
def simulate_name_version(name, version=None):
    try:
        query = dict(request.json)
    except TypeError:
        return error(412, "request must contain json input")

    task_id = None
    if '_id' in query:
        task_id = query['_id']
        del query['_id']

    try:
        config = SimulationConfig(name, 'simulations')
        sim = config.get_simulation(version)
        sim = sim.description
        sim['type'] = 'object'
        sim['additionalProperties'] = False
        simcity.parse_parameters(query, sim)
    except HTTPResponse as ex:
        return ex
    except ValueError as ex:
        return error(412, str(ex))
    except EnvironmentError as ex:
        return error(500, ex.message)

    task_props = {
        'name': name,
        'command': sim['command'],
        'arguments': sim.get('arguments', []),
        'parallelism': sim.get('parallelism', '*'),
        'version': version,
        'input': query,
    }
    if 'ensemble' in query:
        task_props['ensemble'] = query['ensemble']
    if 'simulation' in query:
        task_props['simulation'] = query['simulation']

    if task_id is not None:
        task_props['_id'] = task_id

    try:
        token = simcity.add_task(task_props)
    except ResourceConflict:
        return error(409, "simulation name " + task_id + " already taken")

    try:
        simcity.submit_if_needed(config_sim['default_host'], 1)
    except:
        pass  # too bad. User can call /explore/job.

    response.status = 201  # created
    url = '{0}/simulation/{1}'.format(prefix, token.id)
    response.set_header('Location', url)
    return token.value


@get(prefix + '/schema')
def schema_list():
    files = listfiles('schemas')
    return {'schemas': [f[:-5] for f in files if f.endswith('.json')]}


@get(prefix + '/schema/<name>')
def schema_name(name):
    return static_file(name + '.json', mimetype='application/json',
                       root=os.path.join(project_dir, 'schemas'))


@get(prefix + '/resource')
def resource_list():
    files = listfiles('resources')
    return {"resources": [f[:-5] for f in files if f.endswith('.json')]}


@get(prefix + '/resource/<name>')
def resource_name(name):
    return static_file(name + '.json', mimetype='application/json',
                       root=os.path.join(project_dir, 'resources'))


@get(prefix + '/view/totals')
def overview():
    try:
        return simcity.overview_total()
    except:
        return error(500, "cannot read overview")


@post(prefix + '/job')
def submit_job():
    host = request.query.get('host', default=config_sim['default_host'])
    try:
        job = simcity.submit_if_needed(host, int(config_sim['max_jobs']))
    except ValueError:
        return error(404, "Host " + host + " unknown")
    except IOError:
        return error(502, "Cannot connect to host")
    else:
        if job is None:
            response.status = 503  # service temporarily unavailable
        else:
            response.status = 201  # created
            return {key: job[key] for key in ['_id', 'batch_id', 'hostname']}


@get(prefix + '/view/simulations/<name>/<version>')
def simulations_view(name, version):
    ensemble = request.query.get('ensemble')
    config = SimulationConfig(name, 'simulations')
    sim = config.get_simulation(version)
    version = sim.version
    db = simcity.get_task_database()
    design_doc = simcity.ensemble_view(db, name, version, ensemble=ensemble)

    return view_to_json(db.view('all_docs', design_doc=design_doc))


@get(prefix + '/view/jobs')
def jobs_view():
    return view_to_json(simcity.get_job_database().view('active_jobs'))


@get(prefix + '/simulation/<id>')
def get_simulation(id):
    try:
        return simcity.get_task_database().get(id)
    except ValueError:
        return error(404, "simulation does not exist")


@get(prefix + '/simulation/<id>/<attachment>')
def get_attachment(id, attachment):
    try:
        task = simcity.get_task(id)
    except ValueError:
        return error(404, "simulation does not exist")

    if attachment in task.attachments:
        url = simcity.get_task_database().url.rstrip('/')

        if 'public_url' in couch_cfg:
            url = couch_cfg['public_url'] + couch_cfg['database']

        response.status = 302  # temporary redirect
        response.set_header('Location',
                            '{0}/{1}/{2}'.format(url, id, attachment))
    elif attachment in task.files:
        download_dir = tempfile.mkdtemp()
        simcity.download_attachment(task, download_dir, attachment)
        content_type = task.files[attachment].get('content_type', 'auto')
        return static_file(attachment, mimetype=content_type,
                           root=download_dir)
    else:
        return error(404, "attachment not found")


@delete(prefix + '/simulation/<id>')
def del_simulation(id):
    rev = request.query.get('rev')
    if rev is None:
        rev = request.get_header('If-Match')
    if rev is None:
        return error(409, "revision not specified")

    task = simcity.Document({'_id': id, '_rev': rev})

    try:
        simcity.get_task_database().delete(task)
        return {'ok': True}
    except Unauthorized:
        return error(401, "unauthorized")
    except ResourceNotFound:
        return error(404, "document not found")
    except ResourceConflict:
        return error(409, "resource conflict")
    except PreconditionFailed:
        return error(412, "precondition failed")
    except ServerError:
        return error(502, "CouchDB connection failed")


@get(prefix + '/hosts')
def get_hosts():
    hosts = {}
    for section in simcity.get_config().sections():
        if section.endswith('-host'):
            host_name = section[:-5]
            hosts[host_name] = {}
            if config_sim.get('default_host') == host_name:
                hosts[host_name]['default'] = True

    return hosts

if __name__ == '__main__':
    run(host='localhost', port=9090, server='gevent')
