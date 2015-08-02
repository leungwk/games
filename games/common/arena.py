import random
import datetime
import json

class Arena(object):
    """Plays two agents against each other, and tracks the game stats"""
    def __init__(self, state_f, agent_first_f, agent_second_f, **kwargs):
        ## initalizers (TODO: change to have a reset() function in game state and agent)
        self.state_f = state_f
        self.agent_first_f = agent_first_f
        self.agent_second_f = agent_second_f
        ##
        self.move_hist = []
        self.seed = kwargs.get('seed', None)
        self.verbose = kwargs.get('verbose', True)
        self.num_games = kwargs.get('num_games', 1)
        self.arena_output_results = kwargs.get('arena_output_results', True)
        self.output_dir = kwargs.get('output_dir', './')


    def play(self):
        for _ in range(self.num_games):
            self.state = self.state_f()
            self.agent_first = self.agent_first_f()
            self.agent_second = self.agent_second_f()
            self._play_round()
            if self.arena_output_results:
                output_path = self.output_dir +'arena.' +datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
                self.output_results(output_path)


    def _play_round(self):
        if self.verbose:
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
            if self.verbose:
                print(self.state._board)
                print('turn: {}'.format(self.state.turn))
                print()

            if self.state.terminal(agent_cur.colour): # presumably one cannot win the game just by starting, hence no check before the first move
                ## do not look at .turn, because do_move might or might not automatically update .turn
                winner = agent_cur.colour
                break

        self.game_end_time = int(datetime.datetime.now().strftime('%s'))
        self.winner = winner
        if self.verbose:
            print('winner: {}'.format(winner))


    def output_results(self, path_output):
        out_dict = {
            'game_start_time': self.game_start_time,
            'game_end_time': self.game_end_time,
            ## TODO: use custom name for the case of the same agent
            'agent_1': self.agent_first.__class__.__name__,
            'agent_2': self.agent_second.__class__.__name__,
            'params.agent_1': self.agent_first.params(),
            'params.agent_2': self.agent_second.params(),
            'stats.agent_1': self.agent_first.stats(),
            'stats.agent_2': self.agent_second.stats(),
            'winner': str(self.winner),
            'num_ply': len(self.move_hist),
            'move_hist': [(str(pla), str(mov)) for pla, mov in self.move_hist],
            'seed': self.seed,
            }
        with open(path_output, 'w') as pile:
            json.dump(out_dict, pile)
