import random
import time
import pandas as pd
import numpy as np
import doppelgangers_util

"""
    Bruteforce possible values for period length, for number of doppelgangers, etc.
"""

CSV_HEADER = [
    'test_no',
    'tick_size',
    'period',
    'nr_tests',
    'selected_values',
    'distance_id',
    'duration',
    'absolute_return_mean',
    'prediction_accuracy',
    'sign_accuracy',
    'predicted_next',
    'real_next'
]

def test_hypothesis(tick_size, returns, period, nr_tests, select_values, distance, distance_id, test_no):
    time_start = time.time()
    values = {
        'next': [],
        'real_next': []
    }
    diff = []
    signivity = []

    # distance =
    for x in range(nr_tests):
        pos = random.randint(0, len(returns) - period - 2)
        last = returns.iloc[pos:pos + period]

        best, next = doppelgangers_util.predict_next(returns, last, distance, (pos - period, pos + period), select_values)
        real_next = returns.iloc[pos + period]

        values['next'].append(next)
        values['real_next'].append(real_next)

        if (next < 0 and real_next < 0) or (next > 0 and real_next > 0):
            signivity.append(1)
        else:
            signivity.append(0)

        diff.append(abs(next - real_next))

    absolute_return_mean = np.mean(np.absolute(values['real_next']))
    sign_accuracy = np.mean(signivity)
    prediction_accuracy = np.mean(diff)

    time_duration = time.time() - time_start
    print('%d;%s;%d;%d;%d;%d;%.4f;%.4f;%.4f;%.2f;%s;%s' % (
        test_no,
        tick_size,
        period,
        nr_tests,
        select_values,
        distance_id,
        time_duration,
        absolute_return_mean,
        prediction_accuracy,
        sign_accuracy,
        ','.join(map(lambda x: '%.3f' % x, values['next'])),
        ','.join(map(lambda x: '%.3f' % x, values['real_next']))
    ), flush=True)


test_no = 0
tick_sizes = ['hour', 'day', 'week']
periods = range(5, 150, 25)
nr_tests = 50
select_values_range = range(5, 50, 10)

distance = doppelgangers_util.distances_named.values()

# csv header
print(';'.join(CSV_HEADER))

for tick in tick_sizes:
    df = doppelgangers_util.get_data('market_returns.csv', tick)
    returns: pd.Series = df.close - df.open
    for p in periods:
        for select in select_values_range:
            for idx, dist in enumerate(distance):
                test_no += 1
                #try:
                #    test_hypothesis(tick, returns, p, nr_tests, select, dist, idx, test_no)
                #except Exception as e:
                #    print(f'Failed test {test_no} with exception {e}')
