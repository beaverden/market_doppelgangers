import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st
import doppelgangers_util
import bruteforce_stats
import dtw

@st.cache
def get_data(filename, tick_size) -> pd.DataFrame:
    return doppelgangers_util.get_data(filename, tick_size)


def description():
    with open('README.md') as f:
        st.markdown(f.read())


def main():
    st.set_page_config(layout='wide')
    st.sidebar.title('What to show')
    app_mode = st.sidebar.selectbox('Choose app mode', options=[
        'Description',
        'Statistics',
        'Interactive testing',
    ])
    if app_mode == 'Statistics':
        bruteforce_stats.bruteforce_stats()
    elif app_mode == 'Interactive testing':
        interactive_mode()
    elif app_mode == 'Description':
        description()


def interactive_mode():
    st.header('Returns doppelgangers')
    tick_size = st.sidebar.selectbox(label='Tick size', options=['hour', 'day', 'week'])

    df = get_data('market_returns.csv', tick_size)
    returns: pd.Series = df.close - df.open

    st.subheader(f'Timeframe: (`{df.iloc[0].name}` to `{df.iloc[-1].name}`)')
    period = st.sidebar.slider(
        label='Select period to sample (how many ticks)',
        min_value=5,
        max_value=150,
        value=20,
        step=10
    )

    nr_tests = st.sidebar.slider(
        label='Nr random samples to test hypothesis',
        min_value=5,
        max_value=500,
        value=25,
        step=20
    )

    nr_select = st.sidebar.slider(
        label='Find N closest doppelgangers',
        min_value=5,
        max_value=50,
        value=5,
        step=10
    )

    distance_fn = st.sidebar.selectbox(label='Distance function',
                                       options=list(doppelgangers_util.distances_named.keys()))
    distance = doppelgangers_util.distances_named[distance_fn]

    check_min_distnace = st.sidebar.checkbox(label='Check only below threshold distance')
    min_distance = None
    if check_min_distnace:
        min_distance = st.sidebar.number_input(
            label="Minimum distance to consider",
            min_value=1.0,
            step=1.0,
            value=0.3 * period
        )

    values = {
        'next': [],
        'real_next': []
    }
    diff = []
    signivity = []

    st.subheader(f'Sampling `{nr_tests}` values')

    progress_bar = st.progress(0)
    best_match_period = None
    best_match_dopple = None
    best_match_dist = None

    not_suited_value_cnt = 0
    for x in range(nr_tests):
        progress_bar.progress((x + 1) * (1 / nr_tests))

        pos = random.randint(0, len(returns) - period - 2)
        last = returns.iloc[pos:pos + period]

        best, next = doppelgangers_util.predict_next(returns, last, distance, (pos - period, pos + period),
                                                     nr_select, min_distance)
        if next is None:
            not_suited_value_cnt += 1
            continue

        best_dist, best_pos = best

        if best_match_dist is None or best_dist < best_match_dist:
            best_match_dist = best_dist
            best_match_period = returns.iloc[pos:pos + period + 1]
            best_match_dopple = returns.iloc[best_pos:best_pos + period + 1]

        real_next = returns.iloc[pos + period]

        values['next'].append(next)
        values['real_next'].append(real_next)

        if (next < 0 and real_next < 0) or (next > 0 and real_next > 0):
            signivity.append(1)
        else:
            signivity.append(0)

        diff.append(abs(next - real_next))

        # print(next, real_next)

    if len(values['next']) == 0:
        st.write('Nothing to show')
        return

    absolute_return_mean = np.mean(np.absolute(values['real_next']))
    sign_accuracy = np.mean(signivity)
    prediction_accuracy = np.mean(diff)

    st.subheader('Statistics')
    if check_min_distnace:
        st.markdown(f'Found `{len(values["next"])}` that match the distance criteria')
        st.markdown(f'Rejected `{not_suited_value_cnt}` tests')

    st.markdown(f'Mean absolute return `{absolute_return_mean}`')
    st.markdown(f'Mean return difference between predicted value and real value `{prediction_accuracy}`')
    st.markdown(f'Sign prediction accuracy `{sign_accuracy * 100}%`')

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))
    ax1.set_title('Sample return values plot')
    ynext = values['next']
    ax1.plot(ynext, label='predicted next return')
    yreal = values['real_next']
    ax1.plot(yreal, label='real next return')
    ax1.legend()
    ax1.set_ylabel('Return')
    ax1.set_xlabel('Observation index')

    ax2.set_title('Closest distance between 2 periods %.4f' % best_match_dist)
    ax2.set_xlabel('Period ticks (+ last bonus tick of out of sample next values)')
    ax2.set_ylabel('Return')
    ax2.plot(best_match_period.values, label=best_match_period.index[0])
    ax2.plot(best_match_dopple.values, label=best_match_dopple.index[0])
    ax2.legend()

    st.pyplot(fig)


main()
