import os
import datetime
import pprint
pp = pprint.PrettyPrinter(indent = 4)
from google.cloud import bigquery
import pandas as pd

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

from jinja2 import Environment, select_autoescape, FileSystemLoader

from henry_covid19 import common

DIR = os.path.split(os.path.abspath(__file__))[0]

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)


"""
makes graphs for rates of states compared to US
logarithmic graphs
"""

def get_state_data():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states_cum.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    return df

def get_us_data():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'us.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    return df

def make_state_graph(df_state, df_us, min_values, state, 
        plot_height = 300, plot_width = 300, key = 'deaths', use_log = True):
    if use_log:
        p = figure (y_axis_type = 'log', 
                title = '{state}'.format(state = state),
                 plot_width=plot_width, 
                 plot_height=plot_height)
    else:
        p = figure (title = '{state}'.format(state = state),
                 plot_width=plot_width, 
                 plot_height=plot_height)
    df_state = df_state[(df_state['state']==state) & ( df_state[key] > min_values)]
    df_us = df_us[(df_us['deaths'] > min_values)]
    p.line(x= range(len(df_state[key].tolist())),  y=df_state[key].tolist(), color='green', 
           legend_label = state, line_width = 2)
    seven_day = common.double_rate_line(start = min_values, rate =  7, 
            the_len = len(df_us[key].tolist()))
    two_day = common.double_rate_line(start = min_values, rate =  3, 
            the_len = len(df_us[key].tolist()))
    if use_log:
        p.line(x= range(len(df_us[key].tolist())),  y=df_us[key].tolist(), color='gray',
           legend_label = 'US')

        p.line(x = range(len(df_us[key].tolist())), y = seven_day, legend_label = '7 days',
           line_dash = 'dashed')
        p.line(x = range(len(df_us[key].tolist())), y = two_day, legend_label = '3 days',
           line_dash = 'dashed')
    p.legend.location = 'top_left'
    p.yaxis.formatter=NumeralTickFormatter(format="0,")

    return p

def all_states(df_state, df_us, key_territory, key, use_log):
    states = sorted(set(df_state[key_territory].tolist()))
    p_list = []
    for i in states:
        p_list.append(make_state_graph(df_state = df_state, 
            df_us = df_us, min_values = 10, state = i, key = key, 
            use_log = use_log))
    grid = gridplot(p_list, ncols = 4)
    return grid

def get_html(script, div, the_type):
    """
    Create the HTML
    """
    if the_type == 'deaths':
        title = 'Growth of rates of deaths'
    elif the_type == 'cases':
        title = 'Growth of rates of cases'
    t = ENV.get_template('data.j2')
    return t.render(page_title = title,
            script =  script,
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            page_class_attr = ["deathRateGrowth"],
            div = div,
            )
def main():
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    df_states = get_state_data()
    df_us = get_us_data()
    for i in [('deaths', 'states-deaths', True),
            ('cases', 'states-cases', True),
            ('deaths', 'states-deaths-lin', False),
            ('cases', 'states-cases-lin', False),
            ]:
        grid = all_states(df_states, df_us, key_territory = 'state', 
                key = i[0], use_log = i[2])
        script, div = components(grid)
        html = get_html(script, div, the_type = 'deaths')
        with open(os.path.join('html_temp', i[1]), 'w') as write_obj:
            write_obj.write(html)

if __name__ == '__main__':
    main()
