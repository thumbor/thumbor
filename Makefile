run: compile_ext
	@thumbor -l debug

setup:
	@pip install Cython==0.22
	@pip install numpy==1.9.2
	@pip install https://github.com/scikit-image/scikit-image/archive/master.zip
	@pip install -e .[tests]
	@echo
	@echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	@echo ">>>>>>>>>>>>>>> MAKE SURE GIFSICLE IS INSTALLED IF RUNNING TESTS <<<<<<<<<<<<<<"
	@echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
	@echo

compile_ext:
	@python setup.py build_ext -i

f ?= "vows/"
test pyvows: compile_ext redis
	@pyvows -vv --profile --cover --cover-package=thumbor --cover-threshold=90 $f
	@$(MAKE) unit coverage
	@nosetests -sv thumbor/integration_tests/
	@$(MAKE) static
	$(MAKE) kill_redis

ci_test: compile_ext
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@echo "TORNADO IS `python -c 'import tornado; import inspect; print(inspect.getfile(tornado))'`"
	@echo "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
	@if [ -z "$$INTEGRATION_TEST" ]; then $(MAKE) pyvows_run unit static coverage; else $(MAKE) integration_run; fi

pyvows_run:
	@pyvows -vvv --profile --cover --cover-package=thumbor --cover-threshold=90 vows/

integration_run:
	@nosetests -sv thumbor/integration_tests/

coverage:
	@coverage report -m --fail-under=10

unit:
	@coverage run --branch `which nosetests` -v --with-yanc -s tests/

unit-parallel:
	@`which nosetests` -v --with-yanc --processes=4 -s tests/

focus:
	@coverage run --branch `which nosetests` -vv --with-yanc --logging-level=WARNING --with-focus -i -s tests/


mysql_test: pretest
	PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests/test_mysql_storage.py

kill_redis:
	@-redis-cli -p 6668 -a hey_you shutdown

redis: kill_redis
	@redis-server redis.conf ; sleep 1
	@redis-cli -p 6668 -a hey_you info

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
