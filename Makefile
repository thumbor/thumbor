run: compile_ext
	@PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py -l debug

compile_ext:
	python setup.py build_ext -i

test pyvows: compile_ext redis mongo
	@PYTHONPATH=.:$$PYTHONPATH pyvows -v --profile --cover --cover_package=thumbor --cover_threshold=90 vows/
	@make kill_mongo kill_redis

mysql_test: pretest
	@PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests/test_mysql_storage.py

kill_mongo:
	@ps aux | awk '(/mongod/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

mongo: kill_mongo
	@rm -rf /tmp/thumbor/mongodata && mkdir -p /tmp/thumbor/mongodata
	@mongod --dbpath /tmp/thumbor/mongodata --logpath /tmp/thumbor/mongolog --port 7777 --quiet &

kill_redis:
	@ps aux | awk '(/redis-server/ && $$0 !~ /awk/){ system("kill -9 "$$2) }'

redis: kill_redis
	@redis-server redis.conf &
