.PHONY: all requirements test-requirements test clean pyflakes pyflakes-exists unittest unittest-coverage fulltest install reinstall serve check-couchdb-env docker docker-run docker-osmium docker-couchdb docker-base docs minify

all: install

requirements:
	@pip install Cython
	@pip install -r requirements.txt

test-requirements:
	@pip install -r test_requirements.txt > /dev/null

install: requirements minify
	@pip install .

reinstall:
	@pip install --upgrade --no-deps .

pyflakes:
	@echo "======= PyFlakes ========="
	@find simcityweb -name '*.py' -exec pyflakes {} \;
	@find scripts -name '*.py' -exec pyflakes {} \;
	@find tests -name '*.py' -exec pyflakes {} \;

unittest:
	@echo "======= Unit Tests ========="
	@nosetests

test: test-requirements pyflakes unittest

unittest-coverage:
	@echo "======= Unit Tests ========="
	@nosetests --with-coverage --cover-package=simcityweb

fulltest: test-requirements pyflakes unittest-coverage

clean: 
	rm -rf build/
	find . -name *.pyc -delete
	find . -name *.pyo -delete

serve-dev:
	python -m bottle scripts.app --debug --reload --bind localhost:9090 -s gevent

serve: minify
	python -m bottle scripts.app --bind localhost:9090 -s gevent

COUCHDB_CONFIG = docker/couchdb/local.ini couchdb.env
OSMIUM_CONFIG = docker/osmium/joblauncher.yml docker/osmium/ssh_config docker/osmium/ssh_key docker/osmium/ssh_key.pub docker/osmium/ssh_known_hosts
WEBSERVICE_CONFIG = docker/webservice/config.ini

$(COUCHDB_CONFIG) $(OSMIUM_CONFIG) $(WEBSERVICE_CONFIG):
	python configure-docker.py

docker-couchdb: $(COUCHDB_CONFIG) docker/couchdb/Dockerfile
	docker build -t simcity/couchdb docker/couchdb

docker-osmium: $(OSMIUM_CONFIG) docker/osmium/Dockerfile
	docker build -t simcity/osmium docker/osmium

docker: docker-base $(WEBSERVICE_CONFIG) docker/webservice/Dockerfile
	docker build -t simcity/webservice docker/webservice

docker-base: docker/webservice-base/Dockerfile docker/webservice-base/start.sh
	docker build -t nlesc/simcitywebservice docker/webservice-base

check-couchdb-env: $(COUCHDB_CONFIG)
ifndef COUCHDB_USERNAME
	$(error COUCHDB_USERNAME environment variable is not set. Run ". couchdb.env")
endif
ifndef COUCHDB_PASSWORD
	$(error COUCHDB_PASSWORD environment variable is not set. Run ". couchdb.env")
endif

docker-run: check-couchdb-env docker docker-osmium docker-couchdb
	docker run --name osmium -d simcity/osmium
	docker run --name couchdb -d -p 5984:5984 simcity/couchdb
	docker run --name simcitywebservice -d -e COUCHDB_USERNAME -e COUCHDB_PASSWORD -p 9090:9090 --link couchdb:couchdb --link osmium:osmium simcity/webservice

docker-clean:
	docker rm -f osmium couchdb simcitywebservice

docs: docs/apiary.apib
	aglio -i docs/apiary.apib -o docs/apiary.html
	apib2swagger -i docs/apiary.apib -o docs/swagger.json

SIMULATIONS = simulations/matsim.json simulations/transims-us101.json
SCHEMAS = schemas/point2d.json
JSON_MINIFY = json-minify
JSON_MINIFY_INSTALL = install json-minify with npm install -g json-minify

minify: $(patsubst %.json, %.min.json, $(SIMULATIONS) $(SCHEMAS))

# Only write to minified file if json-minify exists
# See http://stackoverflow.com/questions/592620/check-if-a-program-exists-from-a-bash-script
%.min.json: %.json
	@echo "$(JSON_MINIFY) $< > $@"
	@sh -c "if command -v $(JSON_MINIFY) >/dev/null; then if $(JSON_MINIFY) $< > $@.tmp; then mv $@.tmp $@; else rm $@.tmp; exit 1; fi; else echo 'WARNING: $(JSON_MINIFY_INSTALL)'; fi"
