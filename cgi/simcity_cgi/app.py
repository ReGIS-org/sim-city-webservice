from bottle import post, get, run, request, response, HTTPResponse
import simcity
from simcity.task import Token
from util import abort, error, get_simulation_config
from parameter import parse_parameters

simcity_client.init('../../config.ini')
config = simcity_client.config
config_sim = config.section('Simulations')

@get('/app/simulate/<name>/<version>')
def get_simulation_by_name_version( name, version = None ):
    try:
        sim, version = get_simulation_config(name, version, config_sim)
        return sim[version]
    except HTTPResponse as ex:
        return ex

@get('/app/simulate/<name>')
def get_simulation_by_name( name ):
    try:
        sim, version = get_simulation_config(name, None, config_sim)
        return sim
    except HTTPResponse as ex:
        return ex
    
@post('/app/simulate/<name>/<version>')
def simulate_name_version( name, version = None ):
    try:
        sim, version = get_simulation_config(name, version, config_sim)
        sim = sim[version]
        params = parse_parameters(dict(request.forms), cursim['parameters'])
    except HTTPResponse as ex:
        return ex
    
    token = simcity.task.add({
        'command': cursim['command'],
        'version': version,
        'input': params
    })
    
    couch_cfg = config.section('CouchDB')
    response.status = 201 # created
    response.set_header('Location', couch_cfg['url'] + couch_cfg['database'] + '/' + token.id)
    return token.value

@post('/app/simulate/<name>')
def simulate_name( name ):
    return simulate_name_version(name)

@get('/app/overview')
def overview():
    try:
        return simcity_client.overview_total()
    except:
        return error(500, "cannot read overview")

run(host='localhost', port=9090, debug=True, reloader=True)
