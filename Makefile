.PHONY: all requirements test-requirements test clean pyflakes pyflakes-exists unittest unittest-coverage fulltest install reinstall serve

all: install

requirements:
	@pip install -r requirements.txt

test-requirements:
	@pip install -r test_requirements.txt > /dev/null

install: requirements
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
	@nosetests --with-coverage

fulltest: test-requirements pyflakes unittest-coverage

clean: 
	rm -rf build/
	find . -name *.pyc -delete
	find . -name *.pyo -delete

serve-dev:
	python -m bottle scripts.app --debug --reload --bind localhost:9090 -s gevent

serve:
	python -m bottle scripts.app --bind localhost:9090 -s gevent

docker-couchdb: docker/couchdb/local.ini docker/couchdb/Dockerfile
	docker build -t simcity/couchdb docker/couchdb

docker-osmium: docker/osmium/Dockerfile docker/osmium/joblauncher.yml docker/osmium/ssh_config docker/osmium/ssh_known_hosts
	docker build -t simcity/osmium docker/osmium

docker: docker-base docker/webservice/config.ini docker/webservice/Dockerfile
	docker build -t simcity/webservice docker/webservice

docker-base: docker/webservice-base/Dockerfile docker/webservice-base/start.sh
	docker build -t nlesc/simcitywebservice docker/webservice-base

docker-run: docker docker-osmium docker-couchdb
	docker run --name osmium -d simcity/osmium
	docker run --name couchdb -d -p 5984:5984 simcity/couchdb
	docker run --name simcitywebservice -d -e COUCHDB_USERNAME -e COUCHDB_PASSWORD -p 9090:9090 --link couchdb:couchdb --link osmium:osmium simcity/webservice
