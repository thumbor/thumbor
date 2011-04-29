run:
	@PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py -l debug

test:
	@PYTHONPATH=.:$$PYTHONPATH nosetests -v -s --with-coverage --cover-erase --cover-package=thumbor tests

pyvows:
	@PYTHONPATH=.:$$PYTHONPATH pyvows vows/
