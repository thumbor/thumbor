run:
	PYTHONPATH=.:$$PYTHONPATH python thumbor/app.py

test:
	nosetests -v -s tests
