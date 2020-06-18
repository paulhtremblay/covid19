import os
import datetime

import pandas as pd
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.embed import components

from jinja2 import Environment, select_autoescape, FileSystemLoader

from henry_covid19 import common

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)


def _get_state_df():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states.csv')
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def _get_pop_df():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states_population.csv')
    df = pd.read_csv(path)
    return df

def incidents_over_time_bar(df, key, window= 3, plot_height = 600,
             plot_width = 600, title = None, line_width = 2, y_range = None,
                           x_range=None):
    labels = df['date'].tolist()
    if isinstance(labels[0], datetime.date):
        labels = [datetime.datetime(x.year, x.month, x.day) for x in labels]
    nums = df[key].rolling(window).mean()
    p = figure(x_axis_type = 'datetime', title = title,
                 plot_width = plot_width , plot_height = plot_height, y_range = y_range,
              x_range = x_range)
    p.vbar(x=labels, top=nums, line_width = line_width, width = .9)
    return p

def shape_data(df, df_pop, state):
    df_s = df[df['state'] == state]
    pop = df_pop[df_pop['state'] == state]['population_2019'].tolist()
    #df_s['deaths_pop'] = df_s.loc[:, 'deaths'] * (1e6 / pop[0] )
    df_s = df_s.assign(deaths_pop = df_s['deaths'] * (1e6/pop[0]))
    df_s = df_s.assign(cases_pop = df_s['cases'] * (1e6/pop[0]))
    return df_s

def append_to_graph(df, l, title, keyword = 'cases_pop', max_y = 600):
    l.append(incidents_over_time_bar(df, keyword, plot_width = 300,
    plot_height = 300, title = title, y_range = (0,max_y),
    x_range = (datetime.datetime(2020,3, 1) , datetime.datetime(2020,6, 20))
    ))

def make_dir(key):
    dir_path = os.path.join('html_temp', key)
    if not os.path.isdir(dir_path):
        print(dir_path)
        os.mkdir(dir_path)
    return dir_path

def get_html(date, script, div):

    """
    Create the HTML  
    """
    t = ENV.get_template('countries.j2')
    return t.render( script =  script,
            date = date,
            div = div,
            )

def make_state_graphs():
    date = datetime.datetime.now()
    df_pop = _get_pop_df()
    df_state = _get_state_df()
    l = []
    info = [('Arizona',),
           ('Texas',),
            ('Arkansas',),
            ('Florida',),
            ('California',),
            ('North Carolina',),
            ('Georgia',),
            ('Kentucky',),
            ('Tennessee',),
           ]
    df_ny = shape_data(df = df_state, df_pop = df_pop, state = 'New York')
    df_wash = shape_data(df = df_state, df_pop = df_pop, state = 'Washington')
    for i in info:
        df_ = shape_data(df = df_state, df_pop = df_pop, state = i[0])
        append_to_graph(shape_data(df = df_state, df_pop = df_pop, state = i[0]), l, i[0])
        append_to_graph(df_wash, l, 'Washington')
        append_to_graph(df_ny, l, 'New york')
    grid = gridplot(l, ncols = 3)
    #show(grid)
    script, div = components(grid)
    html = get_html(script = script, div = div, date = date)
    with open(os.path.join('html_temp', 'comparisons'), 'w') as write_obj:
        write_obj.write(html)

if __name__ == '__main__':
    make_state_graphs()
