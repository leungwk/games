# even though py.test says "collected 0 items", they were run
test: test_conga test_other test_rith

GAMES_MODULE_DIR=./games

test_conga:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} py.test-3.4 tests/test_conga.py

test_conga_play:
	python3 $(GAMES_MODULE_DIR)/conga.py --black RandomAgent --white AlphaBetaAgent # does it crash?

test_other:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} py.test-3.4 tests/common/test_board.py tests/search/test_conga.py tests/search/test_mcts.py tests/search/test_alphabeta.py

profile:
	pprofile $(GAMES_MODULE_DIR)/profile_mcts.py > data/profile/profile.out

test_rith:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} py.test-3.4 tests/test_rith.py

test_rith_play:
	python3 $(GAMES_MODULE_DIR)/rith.py
