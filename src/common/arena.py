import random
import datetime
import json

class Arena(object):
    """"""
    def __init__(self, state, agent_first, agent_second, **kwargs):
        ## these need to have already been constructed
        self.state = state
        self.agent_first = agent_first
        self.agent_second = agent_second
        self.move_hist = []
        ##
        self.seed = None
        # self.verbose = False
        for key, value in kwargs.items():
            if key == 'seed':
                self.seed = value
            elif key == 'verbose':
                self.verbose = value


    def play(self):
        print("Game start: ")
        print(self.state._board)
        print('Turn: {}'.format(self.state.turn))
        print()

        random.seed(self.seed)

        self.game_start_time = int(datetime.datetime.now().strftime('%s'))

        while True:
            ## assuming a 2 player game (for now)
            if self.agent_first.colour == self.state.turn:
                agent_cur = self.agent_first
            else:
                agent_cur = self.agent_second
            move = agent_cur.decision(self.state)
            self.state.do_move(move)
            ## tracking
            self.move_hist.append((agent_cur.colour, move))
            ## display
            print(self.state._board)
            print('turn: {}'.format(self.state.turn))
            print()

            if self.state.terminal(agent_cur.colour): # presumably one cannot win the game just by starting, hence no check before the first move
                winner = agent_cur.colour
                break

        self.game_end_time = int(datetime.datetime.now().strftime('%s'))
        self.winner = winner
        print('winner: {}'.format(winner))


    def output_results(self, path_output):
        out_dict = {
            'start_time_game': self.game_start_time,
            'end_time_game': self.game_end_time,
            ## TODO: use custom name for the case of the same agent
            'agent_1': self.agent_first.__class__.__name__,
            'agent_2': self.agent_second.__class__.__name__,
            'params_agent_1': self.agent_first.params(),
            'params_agent_2': self.agent_second.params(),
            'winner': str(self.winner),
            'num_ply': len(self.move_hist),
            'move_hist': [(str(pla), str(mov)) for pla, mov in self.move_hist],
            'seed': self.seed,
            }
        with open(path_output, 'w') as pile:
            json.dump(out_dict, pile)
