import pandas as pd
import numpy as np
import scipy.stats
import scipy.spatial
import heapq
import dtw

# Loads the data from CSV
# If tick_size is day or week, the data is upsampled
def get_data(filename, tick_size) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df.datetime = pd.to_datetime(df.datetime, format='%Y-%m-%d %H:%M:%S')
    df.set_index('datetime', inplace=True)

    if tick_size == 'day':
        df = df.resample('1D').agg({
            'open': 'first',
            'close': 'last',
            'high': 'max',
            'low': 'min',
            'volume': 'sum',
            'openinterest': 'sum'
        })
        df.dropna(inplace=True)
    elif tick_size == 'week':
        df = df.resample('1W').agg({
            'open': 'first',
            'close': 'last',
            'high': 'max',
            'low': 'min',
            'volume': 'sum',
            'openinterest': 'sum'
        })
        df.dropna(inplace=True)
    return df


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


# - returns is the overal market returns with the same tick size as the period
# - period is the series for which we're searching doppelgangers
# - avoid a tuple of values, the [A, B] range of periods that should be avoided
#   it is used to stop the algorithm from picking the selected period as its doppelganger
# - nr_select is the maximum number of doppelgangers it's allowed to pick
# - if min_distance is specified, it won't pick doppelgangers with a distance bigger than that
#   sacrificing nr_select sometimes (there may be fewer than desired)
def predict_next(returns: pd.Series, period: pd.Series, distance, avoid, nr_select, min_distance=None):
    doppels = []
    period_len = len(period)
    avoid_low, avoid_high = avoid
    for pos in range(len(returns) - period_len - 1):
        if avoid_low <= pos <= avoid_high:
            continue

        possible_doppel = returns.iloc[pos:pos + period_len]
        dist = distance(possible_doppel.values, period.values)

        if min_distance is None or dist < min_distance:
            doppels.append((dist, pos))

    if len(doppels) == 0:
        return None, None

    smallest = heapq.nsmallest(nr_select, doppels, key=lambda x: x[0])
    next_values = []
    for _, x in smallest:
        # Get the next tick after the period
        next_tick = returns.iloc[x + period_len]
        next_values.append(next_tick)

    if len(next_values) == 1:
        return smallest[0], next_values[0]

    # Also rejection of wild values is possible, but do we really need to reject it?
    return smallest[0], np.mean(np.array(next_values))


distances_named = {
    'cityblock': lambda x, y: scipy.spatial.distance.cityblock(x, y),
    'euclidean': lambda x, y: np.linalg.norm(x - y),
    'minkowski p=3': lambda x, y: scipy.spatial.distance.minkowski(x, y, p=3),
    'minkowski p=4': lambda x, y: scipy.spatial.distance.minkowski(x, y, p=4),
    'dtw': lambda x, y: dtw.dtw(x, y, distance_only=True).distance
}
