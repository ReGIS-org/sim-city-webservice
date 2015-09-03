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

from gevent import monkey; monkey.patch_all()

from bottle import post, get, run, delete, request, response, HTTPResponse
import simcity
from simcity.util import listfiles
from simcityweb.util import error, get_simulation_config
import simcityexplore
from couchdb.http import ResourceConflict
from picas.documents import Document

config_sim = simcity.get_config().section('Simulations')
couch_cfg = simcity.get_config().section('task-db')


@get('/explore/simulate/<name>/<version>')
def get_simulation_by_name_version(name, version=None):
    try:
        sim, version = get_simulation_config(name, version, config_sim)
        return sim[version]
    except HTTPResponse as ex:
        return ex


@get('/explore/simulate/<name>')
def get_simulation_by_name(name):
    try:
        sim, version = get_simulation_config(name, None, config_sim)
        return sim
    except HTTPResponse as ex:
        return ex


@get('/explore')
def explore():
    return "API: overview | simulate | job"


@get('/explore/simulate')
def simulate_list():
    files = listfiles(config_sim['path'])
    return {"simulations": [f[:-5] for f in files if f.endswith('.json')]}


@post('/explore/simulate/<name>/<version>')
def simulate_name_version(name, version=None):
    try:
        sim, version = get_simulation_config(name, version, config_sim)
        sim = sim[version]
        query = dict(request.json)
        task_id = None
        if '_id' in query:
            task_id = query['_id']
            del query['_id']

        params = simcityexplore.parse_parameters(query, sim['parameters'])
    except HTTPResponse as ex:
        return ex
    except ValueError as ex:
        return error(400, ex.message)

    task_props = {
        'name': name,
        'ensemble': query['ensemble'],
        'command': sim['command'],
        'version': version,
        'input': params,
    }

    if task_id is not None:
        task_props['_id'] = task_id

    try:
        token = simcity.add_task(task_props)
    except ResourceConflict:
        return error(400, "simulation name " + task_id + " already taken")

    try:
        simcity.submit_if_needed(config_sim['default_host'], 1)
    except:
        pass  # too bad. User can call /explore/job.

    response.status = 201  # created
    url = '%s%s/%s' % (couch_cfg.get('public_url', couch_cfg['url']),
                       couch_cfg['database'], token.id)
    response.set_header('Location', url)
    return token.value


@post('/explore/simulate/<name>')
def simulate_name(name):
    return simulate_name_version(name)


@get('/explore/view/totals')
def overview():
    try:
        return simcity.overview_total()
    except:
        return error(500, "cannot read overview")


@post('/explore/job')
def submit_job():
    return submit_job_to_host(config_sim['default_host'])


@post('/explore/job/<host>')
def submit_job_to_host(host):
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


@get('/explore/view/simulations/<name>/<version>')
def simulations_view(name, version):
    ensemble_view(name, version, None)
    return


@get('/explore/view/simulations/<name>/<version>/<ensemble>')
def ensemble_view(name, version, ensemble):
    sim, version = get_simulation_config(name, version, config_sim)
    url = '/couchdb/' + couch_cfg['database']
    design_doc = simcityexplore.ensemble_view(
        simcity.get_task_database(), name, version, url, ensemble)

    location = '{}/_design/{}/_view/all_docs' % (url, design_doc)

    response.status = 302  # temporary redirect
    response.set_header('Location', location)
    return


@get('/explore/simulation/<id>')
def get_simulation(id):
    try:
        return simcity.get_task_database().get(id).value
    except ValueError:
        return error(404, "simulation does not exist")


@delete('/explore/simulation/<id>')
def del_simulation(id):
    rev = request.query.get('rev')
    if rev is None:
        rev = request.get_header('If-Match')
    if rev is None:
        return error(409, "revision not specified")

    task = Document({'_id': id, '_rev': rev})

    try:
        simcity.get_task_database().delete(task)
        return {'ok': True}
    except ResourceConflict:
        return error(409, "resource conflict")

run(host='localhost', port=9090, server='gevent')
