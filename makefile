GAMES_MODULE_DIR=./games
DATA_DIR=./data
CMD_PYTEST=py.test-3.4

# even though py.test says "collected 0 items", they were run
test: test_conga test_rith test_search test_other

test_conga:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} $(CMD_PYTEST) tests/test_conga.py

test_search:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} $(CMD_PYTEST) tests/search/test_conga.py tests/search/test_mcts.py tests/search/test_alphabeta.py

test_other:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} $(CMD_PYTEST) tests/common/test_board.py

test_rith:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} $(CMD_PYTEST) tests/test_rith.py tests/search/test_rith_search.py # cannot be named test_rith.py otherwise import file mismatch ...

test_rithbb:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} $(CMD_PYTEST) tests/test_rithbb.py





profile_rith_ab:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} pprofile ./profile/profile_rith_ab.py > $(DATA_DIR)/profile/alphabeta_rith.out

profile_rithbb:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} pprofile ./profile/rith/profile_rithbb.py > $(DATA_DIR)/profile/rithbb.out


conga_ai_play:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/conga/conga.py --black RandomAgent --white AlphaBetaAgent

rith_ai_play:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/rith/rith.py --even AlphaBetaAgent --odd RandomAgent

play_conga_ai:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/conga/conga.py --black AlphaBetaAgent --white PlayerAgent

play_rith_ai:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/rith/rith.py --even PlayerAgent --odd AlphaBetaAgent

play_conga:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/conga/conga.py

play_rith:
	PYTHONPATH=$(GAMES_MODULE_DIR):${PYTHONPATH} python3 $(GAMES_MODULE_DIR)/rith/rith.py
