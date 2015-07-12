# even though py.test says "collected 0 items", they were run
test_conga:
	PYTHONPATH=./src:${PYTHONPATH} py.test-3.4 tests/test_conga.py
