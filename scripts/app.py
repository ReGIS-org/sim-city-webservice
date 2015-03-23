from gevent import monkey; monkey.patch_all()

from bottle import post, get, run, delete, request, response, HTTPResponse
import simcity
from simcity.util import listfiles
from simcityweb.util import error, get_simulation_config
from simcityweb.parameter import parse_parameters
from couchdb.http import ResourceConflict

config_sim = simcity.config.section('Simulations')
couch_cfg = simcity.config.section('task-db')


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
        query = dict(request.query)
        task_id = None
        if '_id' in query:
            task_id = query['_id']
            del query['_id']

        params = parse_parameters(query, sim['parameters'])
    except HTTPResponse as ex:
        return ex

    task_props = {
        'name': name,
        'command': sim['command'],
        'version': version,
        'input': params,
    }

    if task_id is not None:
        task_props['_id'] = task_id

    try:
        token = simcity.task.add(task_props)
    except ResourceConflict:
        return error(400, "simulation name " + task_id + " already taken")

    try:
        simcity.job.submit_if_needed(config_sim['default_host'], 1)
    except:
        pass  # too bad. User can call /explore/job.

    response.status = 201  # created
    url = '%s%s/%s' % (couch_cfg['public_url'], couch_cfg['database'],
                       token.id)
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
        job = simcity.job.submit_if_needed(host, int(config_sim['max_jobs']))
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
    sim, version = get_simulation_config(name, version, config_sim)
    doc_id = '_design/' + name + '_' + version
    try:
        simcity.task.database.get(doc_id)
    except:
        old_design = simcity.task.database.design_doc
        simcity.task.database.design_doc = doc_id
        simcity.task.database.add_view('all_docs', """
function(doc) {
  if (doc.type === "task" && doc.name === "%s" && doc.version === "%s") {
    emit(doc._id, {
      "id": doc._id,
      "rev": doc._rev,
      "url": "%s%s/" + doc._id,
      "error": doc.error,
      "lock": doc.lock,
      "done": doc.done,
      "input": doc.input
    });
  }
}""" % (name, version, '/couchdb/', couch_cfg['database']))
        simcity.task.database.design_doc = old_design

    url = '%s%s/%s/_view/all_docs' % ('/couchdb/',  # couch_cfg['public_url'],
                                      couch_cfg['database'], doc_id)

    response.status = 302  # temporary redirect
    response.set_header('Location', url)
    return


@get('/explore/simulation/<id>')
def get_simulation(id):
    try:
        return simcity.task.database.get(id).value
    except ValueError:
        return error(404, "simulation does not exist")


@delete('/explore/simulation/<id>')
def del_simulation(id):
    rev = request.query.get('rev')
    if rev is None:
        rev = request.get_header('If-Match')
    if rev is None:
        return error(409, "revision not specified")

    task = simcity.task.Task({'_id': id, '_rev': rev})

    try:
        simcity.task.database.delete(task)
        return {'ok': True}
    except ResourceConflict:
        return error(409, "resource conflict")

run(host='localhost', port=9090, server='gevent')
