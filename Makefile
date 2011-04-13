run:
	PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py -l debug

test:
	PYTHONPATH=.:$$PYTHONPATH nosetests -v -s tests
