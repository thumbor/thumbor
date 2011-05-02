run:
	@PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py -l debug

pretest:
	@-mysql -u root -e 'DROP DATABASE IF EXISTS thumbor_tests'
	@-mysql -u root -e 'CREATE DATABASE IF NOT EXISTS thumbor_tests'
	@-mysql -u root -e 'CREATE TABLE IF NOT EXISTS images (url VARCHAR(1000) NOT NULL PRIMARY KEY, contents BLOB NOT NULL, security_key VARCHAR(100) NULL, last_update TIMESTAMP(8))' thumbor_tests

test: pretest
	@PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests

pyvows:
	@PYTHONPATH=.:$$PYTHONPATH pyvows --cover --cover_package=thumbor --cover_omit=thumbor/vendor/* --cover_threshold=90 vows/

mysql_test: pretest
	@PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests/test_mysql_storage.py
