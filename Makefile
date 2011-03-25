run:
	PYTHONPATH=.:$$PYTHONPATH python thumbor/server.py

test:
	nosetests -v -s tests
