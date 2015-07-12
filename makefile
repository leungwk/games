# even though py.test says "collected 0 items", they were run
test: test_conga test_other

test_conga:
	PYTHONPATH=./src:${PYTHONPATH} py.test-3.4 tests/test_conga.py

test_conga_play:
	python3 src/conga.py --black RandomAgent --white AlphaBetaAgent # does it crash?

test_other:
	PYTHONPATH=./src:${PYTHONPATH} py.test-3.4 tests/common/test_board.py tests/search/test_conga.py
