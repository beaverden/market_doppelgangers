## Market doppelgangers
### Hypothesis

Strong: _If the market periods are similar, the next values after the period are similar_

Weak: _If the market periods are similar, the next values after the period have similar direction (sign)_

Take N ticks of the market price, calculate its returns (`close - open`) 
go back in time and try to find the closest periods to it, in hope that they can predict the next tick value.
The closest periods are found using a pairwise distance function between the elements. 

As a weaker version, 
check if the predicted value at least has the same sign as the real value.


### Variables
A number of variables can be changed when experimenting

- __`tick_size`__ indicates whether ticks are `hours`, `days` or `weeks`
- __`period`__ represents the selected `range length in ticks`. For example, a value of 20 means that
you'll be looking at statistics for a 20 tick period, tested on other random intervals with 20 ticks length
- __`selected_values`__ represents how many closest periods the script should take into calculation
when predicting the next tick value. A value of 5 represents: select the closest 5 periods to the given input period
and calculate a mean of their next values
- __`distance`__ is the function to measure distance between market segments
   - 0 `cityblock`
   - 1 `euclidean`
   - 2 `minkowski(p=3)`
   - 3 `minkowski(p=4)`


### Algorithm
Take the specified period, iterate through all the market returns and calculate the distance
between the given period and the market periods. Sort for the smallest distance, take a number of 
closest observations and look at the next tick for each of them. Calculate the mean of those returns
to predict the next tick for the specified period


### App structure

- `Description` is the current page and provides information about the hypothesis
- `Statistics` is the page that shows the result of bruteforcing the model parameters 
(period, distance function, etc). One can select different metrics to show on the graphs
- `Interactive testing` is where you can tweak the model parameters and then perform a specified number of
random tests with random samples to check if they have any market doppelgangers. _Make sure you
let the tests finish before you change the values since streamlit will keep running them even if you 
change the values and you'll have to wait until the test finish to see your results_


### TL;DR result

- The results can be visualized best on the __Statistics__ page on the correlation graphs on
the right. __The mean distance between the predicted results and the actual return is close to
the mean magnitude of returns, which means that they're insignificant at best__
- Even the weak version of the hypothesis seems to not hold, since no matter how we vary the
model parameters, __the sign prediction accuracy seems to exist in the realms of 50%, hence no better
than a coin flip__
