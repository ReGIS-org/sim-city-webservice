from gevent import monkey; monkey.patch_all()

from bottle import post, get, run, request, response, HTTPResponse
import simcity
from simcity.util import listfiles
from simcityweb.util import error, get_simulation_config
from simcityweb.parameter import parse_parameters

config_sim = simcity.config.section('Simulations')

@get('/explore/simulate/<name>/<version>')
def get_simulation_by_name_version( name, version = None ):
    try:
        sim, version = get_simulation_config(name, version, config_sim)
        return sim[version]
    except HTTPResponse as ex:
        return ex

@get('/explore/simulate/<name>')
def get_simulation_by_name( name ):
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
def simulate_name_version( name, version = None ):
    try:
        sim, version = get_simulation_config(name, version, config_sim)
        sim = sim[version]
        params = parse_parameters(dict(request.forms), sim['parameters'])
    except HTTPResponse as ex:
        return ex
    
    token = simcity.task.add({
        'command': sim['command'],
        'version': version,
        'input': params
    })
    
    couch_cfg = simcity.config.section('task-db')
    response.status = 201 # created
    response.set_header('Location', couch_cfg['public_url'] + couch_cfg['database'] + '/' + token.id)
    return token.value

@post('/explore/simulate/<name>')
def simulate_name( name ):
    return simulate_name_version(name)

@get('/explore/overview')
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
        job = simcity.job.submit_if_needed(host, int(config_sim['max_jobs']))
    except ValueError:
        return error(404, "Host " + host + " unknown")
    except IOError:
        return error(502, "Cannot connect to host")
    else:
        if job is None:
            response.status = 503 # service temporarily unavailable
        else:
            response.status = 201 # created
            return {key: job[key] for key in ['_id', 'batch_id', 'hostname']}

run(host='localhost', port=9090, server='gevent')
