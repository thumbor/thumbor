run:
	PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py -l debug

test:
	nosetests -v -s tests
