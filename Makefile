run: compile_ext
	@PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py -l debug -k thumbor/default.key

compile_ext:
	python setup.py build_ext -i

db:
	@mysql -u root -e 'DROP DATABASE IF EXISTS thumbor'
	@mysql -u root -e 'CREATE DATABASE IF NOT EXISTS thumbor'
	@mysql -u root -e 'CREATE TABLE IF NOT EXISTS images (id int NOT NULL PRIMARY KEY, url VARCHAR(1000) NOT NULL, contents BLOB NOT NULL, security_key VARCHAR(100) NULL, detector_data VARCHAR(2000) NULL, last_update TIMESTAMP);' thumbor

pretest:
	@mysql -u root -e 'DROP DATABASE IF EXISTS thumbor_tests'
	@mysql -u root -e 'CREATE DATABASE IF NOT EXISTS thumbor_tests'
	@mysql -u root -e 'CREATE TABLE IF NOT EXISTS images (id int NOT NULL PRIMARY KEY, url VARCHAR(1000) NOT NULL, contents BLOB NOT NULL, security_key VARCHAR(100) NULL, detector_data VARCHAR(2000) NULL, last_update TIMESTAMP);' thumbor_tests

test: pretest
	@PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests

pyvows: compile_ext
	@PYTHONPATH=.:$$PYTHONPATH pyvows -v --profile --cover --cover_package=thumbor --cover_omit=thumbor/vendor/* --cover_threshold=90 vows/

mysql_test: pretest
	@PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests/test_mysql_storage.py
