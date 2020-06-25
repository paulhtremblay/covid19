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

def incidents_over_time_bar(df, df_ny, key, window= 3, plot_height = 600,
             plot_width = 600, title = None, line_width = 2, y_range = None,
                           x_range=None):
    labels = df['date'].tolist()
    labels2 = df_ny['date'].tolist()
    if isinstance(labels[0], datetime.date):
        labels = [datetime.datetime(x.year, x.month, x.day) for x in labels]
    nums = df[key].rolling(window).mean()
    nums2 = df_ny[key].rolling(window).mean()
    p = figure(x_axis_type = 'datetime', title = title,
                 plot_width = plot_width , plot_height = plot_height, y_range = y_range,
              x_range = x_range)
    p.vbar(x=labels, top=nums, line_width = line_width, width = .9)
    p.vbar(x=labels2, top=nums2, line_width = line_width, width = .9, color= 'green',
           alpha = .1, legend_label = "NY")
    if key == 'deaths_pop':
        p.yaxis.axis_label = 'deaths/million'
    else:
        p.yaxis.axis_label = 'cases/million'
    return p

def shape_data(df, df_pop, state):
    df_s = df[df['state'] == state]
    pop = df_pop[df_pop['state'] == state]['population_2019'].tolist()
    #df_s['deaths_pop'] = df_s.loc[:, 'deaths'] * (1e6 / pop[0] )
    df_s = df_s.assign(deaths_pop = df_s['deaths'] * (1e6/pop[0]))
    df_s = df_s.assign(cases_pop = df_s['cases'] * (1e6/pop[0]))
    return df_s

def append_to_graph(df, l, title, df_ny, keyword = 'cases_pop', max_y = 600):
    l.append(incidents_over_time_bar(df = df, key = keyword, 
        df_ny = df_ny, plot_width = 300,
        plot_height = 300, title = title, y_range = (0,max_y),
        x_range = (datetime.datetime(2020,3, 1) , datetime.datetime(2020,6, 20))
    ))

def make_dir(key):
    dir_path = os.path.join('html_temp', key)
    if not os.path.isdir(dir_path):
        print(dir_path)
        os.mkdir(dir_path)
    return dir_path

def get_html(date, script, div, title):

    """
    Create the HTML  
    """
    t = ENV.get_template('comparison.j2')
    return t.render( script =  script,
            date = date,
            div = div,
            title = title,
            )

def make_state_graphs():
    date = datetime.datetime.now()
    df_pop = _get_pop_df()
    df_state = _get_state_df()
    states = list(set(df_state['state']))
    html_paths = {'cases_pop':'comparisons-cases',
            'deaths_pop': 'comparisons-deaths',
            }
    titles = {'cases_pop':'Cases',
            'deaths_pop': 'Deaths',
            }
    exclude = ['New York', 
        'Northern Mariana Islands',
        'Puerto Rico',
        'Virgin Islands',
        'Guam',
    ]
    df_ny = shape_data(df = df_state, df_pop = df_pop, state = 'New York')
    df_wash = shape_data(df = df_state, df_pop = df_pop, state = 'Washington')
    for case in [('cases_pop', 600),  ('deaths_pop', 60)]:
        l = []
        for i in sorted(states):
            if i in exclude:
                continue
            df_ = shape_data(df = df_state, df_pop = df_pop, state = i)
            append_to_graph(shape_data(df_state, df_pop = df_pop, 
                state = i), l, i, keyword = case[0], max_y = case[1],
                df_ny = df_ny)
            #append_to_graph(df_wash, l, 'Washington', keyword = case[0], max_y = case[1])
            #append_to_graph(df_ny, l, 'New york', keyword = case[0], max_y = case[1])
        grid = gridplot(l, ncols = 3)
        script, div = components(grid)
        html = get_html(script = script, div = div, date = date, title = titles[case[0]])
        with open(os.path.join('html_temp', html_paths[case[0]]), 'w') as write_obj:
            write_obj.write(html)

if __name__ == '__main__':
    make_state_graphs()
