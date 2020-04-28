from google.cloud import bigquery
import pandas as pd

import datetime

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

import scipy.optimize as optim

from henry_covid19 import common

def make_state_graph_fit(df, state, 
        plot_height = 300, plot_width = 300, 
        min_value = 10, key = 'deaths'):
    df_state = df[(df['state']==state) & (df[key] > min_value)]
    popt, pcov = optim.curve_fit(f = common.log_func, 
            xdata = range(len(df_state[key])), 
            ydata = df_state[key] )
    r, c, initial = popt[0], popt[1], popt[2]
    dates_extended = common.get_dates_extended(df_state['dates'], 
            datetime.datetime(2020, 6, 1))
    y_hat = [common.log_func(r =r, c = c, initial = initial, t = i) 
            for i in list(range(len(dates_extended))) ]
    p = figure (title = '{state} (deaths = {c})'.format(state = state, 
        c = int(round(c))),  x_axis_type='datetime',
              plot_width = plot_width, plot_height = plot_height)
    p.line(x = df_state['dates'], y = df_state['deaths'], 
            legend_label = 'actual')
    p.line(x = dates_extended, y = y_hat,  
            legend_label = 'fitted', color = 'red')
    p.legend.location = 'bottom_right'
    return p

def all_states(df_state):
  states = sorted(set(df_state['state'].tolist()))
  p_list = []
  for i in states:
    try:
        p_list.append(make_state_graph_fit(df = df_state, state = i))
    except ValueError:
        print('y data is empty?? for {s}'.format(s = i))
  grid = gridplot(p_list, ncols = 4)
  return grid

def main():
    df_states = common.make_dataframe(common.get_state_data())
    grid = all_states(df_states)
    show(grid)


if __name__ == '__main__':
    main()
