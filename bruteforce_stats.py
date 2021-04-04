import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

values = [
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


def errorbar(ax, df, x, y, label):
    datay = df.groupby(by=x).mean()
    dataerr = df.groupby(by=x).std()

    ax.errorbar(df[x].unique(), datay[y], yerr=dataerr[y],
                label=label, ecolor='r', capsize=5)
    ax.set_ylabel(y)
    ax.set_xlabel(x)
    ax.grid(True)
    ax.legend()


def scatter(fig: plt.Figure, ax: plt.Axes, df, x, label):
    datax = df[x].unique()
    cmap = plt.get_cmap('RdYlGn_r')
    sorted_ids = dict([(x, idx) for idx, x in enumerate(sorted(datax))])
    normalized = (datax - min(datax)) / (max(datax) - min(datax))
    colors = cmap(normalized)
    my_colors = df.apply(lambda elem: colors[sorted_ids[elem[x]]], axis=1)

    ax.scatter(df['absolute_return_mean'], df['prediction_accuracy'], c=my_colors, label=label)
    ax.set_ylabel('prediction_accuracy')
    ax.set_xlabel('absolute_return_mean')
    ax.grid(True)
    ax.legend()

    lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
    ]

    # now plot both limits against eachother
    ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)


def bruteforce_stats():
    st.header('Bruteforce statistics')
    st.markdown("""
    - __`period`__ represents the selected `range length in ticks`. For example, a value of 20 means that
    you'll be looking at statistics for a 20 tick period, tested on other random intervals with 20 ticks length
    __possible value: range(5, 150, 25)__ 
    - __`selected_values`__ represents how many closest periods the script should take into calculation
    when predicting the next tick value. A value of 5 represents: select the closest 5 periods to the given input period
    and calculate a mean of their next values. __possible value: range(5, 50, 10)__
    - __`distance_id`__ is the id of the distance function. __possible values__:
       - 0 `cityblock`
       - 1 `euclidean`
       - 2 `minkowski(p=3)`
       - 3 `minkowski(p=4)`
       
    #### Results   
    - __`sign_accuracy`__ is the ratio of when predicted value had the same sign as the real next value (0.55 = 55%)
    - __`prediction_accuracy`__ is the distance between the predicted value and the real value 
    `abs(predicted_next - real_next)`
    - __`absolute_return_mean`__ is the sign-stripped return mean of the test case periods. For example, if 
    there were 100 tests, then there were 100 predicted next values and 100 real next values. `absolute_return_mean`
    is calculated using absolute values of real next returns `np.mean(np.absolute(real_next_values))`
    
    __*__ If you select to show `period` on X, the graph on the right will
    show the `absolute_return_mean and predicted_accuracy` for each of the unique `period` values.
    The colors in this graph represent unique values for that parameter
    
    __*__ The graphs on the left show the mean value for the Y parameter when X parameter is fixed.
    The red bars are the standard deviation for the Y parameter. For example, when the period is 
    fixed with value `20`, (but other variables can move around, the predicted_accuracy mean was `~0.84`
    with the standard deviation of `0.07` (from `~0.91 to ~0.77`)
    """)

    df = pd.read_csv('bruteforce_output.txt', sep=';')
    st.markdown('Total test duration `%.3f hours`' % (df.duration.sum() / 3600))

    x_axis = st.selectbox('What to show on X', options=['period', 'selected_values', 'distance_id'])
    y_axis = st.selectbox('What to show on Y', options=['prediction_accuracy', 'duration', 'absolute_return_mean',
                                                        'sign_accuracy'])

    fig, ((axh, a), (axd, b), (axw, c)) = plt.subplots(nrows=3, ncols=2, figsize=(10, 10))
    hourly = df[df.tick_size == 'hour']
    daily = df[df.tick_size == 'day']
    weekly = df[df.tick_size == 'week']
    errorbar(axh, hourly, x_axis, y_axis, label='hourly')
    errorbar(axd, daily, x_axis, y_axis, label='daily')
    errorbar(axw, weekly, x_axis, y_axis, label='weekly')

    scatter(fig, a, hourly, x_axis, label='hourly')
    scatter(fig, b, daily, x_axis, label='daily')
    scatter(fig, c, weekly, x_axis, label='weekly')
    fig.tight_layout()
    st.pyplot(fig)

