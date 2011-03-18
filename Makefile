run:
	PYTHONPATH=.:$$PYTHONPATH python server.py

test:
	nosetests -v -s tests
