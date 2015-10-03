run: compile_ext
	@thumbor -l debug

setup:
	@pip install -e .[tests]
	@echo
	@echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	@echo ">>>>>>>>>>>>>>> MAKE SURE GIFSICLE IS INSTALLED IF RUNNING TESTS <<<<<<<<<<<<<<"
	@echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	@echo

compile_ext:
	@python setup.py build_ext -i

f ?= "vows/"
test pyvows: compile_ext redis mongo
	@pyvows -vv --profile --cover --cover-package=thumbor --cover-threshold=90 $f
	@$(MAKE) unit coverage
	@nosetests -sv thumbor/integration_tests/
	@$(MAKE) static
	$(MAKE) kill_mongo kill_redis

ci_test: compile_ext
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@echo "TORNADO IS `python -c 'import tornado; import inspect; print(inspect.getfile(tornado))'`"
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@$(MAKE) pyvows_run unit coverage
	@if [ ! -z "$$INTEGRATION_TEST" ]; then $(MAKE) integration_run; fi

pyvows_run:
	@pyvows -vvv --profile --cover --cover-package=thumbor --cover-threshold=90 vows/

integration_run:
	@nosetests -sv thumbor/integration_tests/

coverage:
	@coverage report -m --fail-under=10

unit:
	@coverage run --branch `which nosetests` -v --with-yanc -s tests/

mysql_test: pretest
	PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests/test_mysql_storage.py

kill_mongo:
	@ps aux | awk '(/mongod/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

mongo: kill_mongo
	@rm -rf /tmp/thumbor/mongodata && mkdir -p /tmp/thumbor/mongodata
	@mongod --dbpath /tmp/thumbor/mongodata --logpath /tmp/thumbor/mongolog --port 7777 --quiet --fork --smallfiles
	@mongo --nodb mongo_check_start.js

kill_redis:
	@-redis-cli -p 6668 -a hey_you shutdown

redis: kill_redis
	@redis-server redis.conf ; sleep 1
	@redis-cli -p 6668 -a hey_you info

kill_memcached:
	@ps aux | awk '(/memcached -p 5555 -d/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

memcached: kill_memcached
	@memcached -p 5555 -d

flake:
	@flake8 . --ignore=W801,E501

setup_docs:
	pip install -r docs/requirements.txt

build_docs:
	cd docs && make html

docs: setup_docs build_docs
	python -mwebbrowser file:///`pwd`/docs/_build/html/index.html

static:
	@flake8 --config=./flake8 .
