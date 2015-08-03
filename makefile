# even though py.test says "collected 0 items", they were run
test: test_conga test_other test_rith

GAMES_MODULE_DIR=./games
DATA_DIR=./data

test_conga:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} py.test-3.4 tests/test_conga.py

test_conga_play:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/conga/conga.py --black RandomAgent --white AlphaBetaAgent

test_other:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} py.test-3.4 tests/common/test_board.py tests/search/test_conga.py tests/search/test_mcts.py tests/search/test_alphabeta.py

test_rith:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} py.test-3.4 tests/test_rith.py tests/search/test_rith_search.py # cannot be named test_rith.py otherwise import file mismatch ...

test_rith_play:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/rith/rith.py

test_profile_rith_ab:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} pprofile ./profile/profile_rith_ab.py > $(DATA_DIR)/profile/alphabeta_rith.out
