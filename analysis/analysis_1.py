import os
import datetime
import json
from collections import defaultdict

def _isodate_to_unix(isodate):
    return int(datetime.datetime.strptime(isodate, '%Y-%m-%d %H:%M:%S').strftime('%s'))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--log-start-date', type=str, default='')
    parser.add_argument('--log-end-date', type=str, default='')
    parser.add_argument('--data-dir')
    parser.add_argument('--player-1', type=str, default='')
    parser.add_argument('--player-2', type=str, default='')
    args = parser.parse_args()

    player_1, player_2 = args.player_1, args.player_2

    log_start_date, log_end_date = args.log_start_date, args.log_end_date
    log_start_date_unix = _isodate_to_unix(log_start_date) if log_start_date else float('-Inf')
    log_end_date_unix = _isodate_to_unix(log_end_date) if log_end_date else float('Inf')

    # "map/reduce"
    def read_files():
        data_dir = args.data_dir
        for filename in [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]:
            with open(os.path.join(data_dir, filename), 'r') as pile:
                record = json.load(pile)
                yield record


    def map_records():
        for record in read_files():
            if log_start_date_unix <= record['game_start_time'] <= log_end_date_unix:
                yield ('winner', (record['winner'], 1))
            if record['agent_2'] == 'AlphaBetaAgent':
                ab_rec = record['stats.agent_2']['alphabeta']
                cache_hit = cache_miss = 0
                for entry in ab_rec:
                    cache_hit += entry['cache_hit']
                    cache_miss += entry['cache_miss']
                yield ('ab_cache', (cache_hit, cache_miss))

    def reduce_records():
        acc_winner = defaultdict(int)
        acc_cache = defaultdict(int)
        for rec_type, tup in map_records():
            if rec_type == 'winner':
                winner, count = tup
                acc_winner[winner] += count
            elif rec_type == 'ab_cache':
                cache_hit, cache_miss = tup
                acc_cache['cache_hit'] += cache_hit
                acc_cache['cache_miss'] += cache_miss
        return acc_winner, acc_cache

    stats_winner, stats_cache = reduce_records()
    tot_runs = sum(stats_winner.values())

    import scipy.stats
    print(stats_winner)
    print(scipy.stats.chisquare(f_obs=[stats_winner[player_1], stats_winner[player_2]], f_exp=[tot_runs/2, tot_runs/2]))
    print
    print(stats_cache)
    print(stats_cache['cache_hit']/sum([v for v in stats_cache.values()]))
