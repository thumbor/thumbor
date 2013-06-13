run: compile_ext
	PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py -l debug

compile_ext:
	python setup.py build_ext -i

f ?= "vows/"
test pyvows: compile_ext redis mongo
	PYTHONPATH=.:$$PYTHONPATH pyvows -vv --profile --cover --cover_package=thumbor --cover_threshold=90 $f
	PYTHONPATH=.:$$PYTHONPATH python -m tornado.test.runtests discover integration_tests/ '*_test.py'
	$(MAKE) kill_mongo kill_redis

ci_test: compile_ext
	$(MAKE) redis mongo
	PYTHONPATH=.:$$PYTHONPATH:/usr/local/lib/python2.6/site-packages:/usr/lib/python2.6/site-packages pyvows -vvv --profile --cover --cover_package=thumbor --cover_threshold=90 vows/
	PYTHONPATH=.:$$PYTHONPATH:/usr/local/lib/python2.6/site-packages:/usr/lib/python2.6/site-packages python -m tornado.test.runtests discover integration_tests/ '*_test.py'
	$(MAKE) kill_mongo kill_redis

mysql_test: pretest
	PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests/test_mysql_storage.py

kill_mongo:
	@ps aux | awk '(/mongod/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

mongo: kill_mongo
	@rm -rf /tmp/thumbor/mongodata && mkdir -p /tmp/thumbor/mongodata
	@mongod --dbpath /tmp/thumbor/mongodata --logpath /tmp/thumbor/mongolog --port 7777 --quiet &
	@sleep 5

kill_redis:
	@-redis-cli -p 7778 -a hey_you shutdown

redis: kill_redis
	@redis-server redis.conf ; sleep 1
	@redis-cli -p 7778 -a hey_you info

flake:
	@flake8 . --ignore=W801,E501
