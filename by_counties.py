import datetime
import os

import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.embed import components

from henry_covid19 import common
from henry_covid19 import variables

from jinja2 import Environment, select_autoescape, FileSystemLoader

ENV = Environment(
    loader=FileSystemLoader(os.path.join(
        os.path.split(os.path.abspath(__file__))[0], 
        'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

def get_county_data():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'seven_day_county.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    return df

def make_counties_dir(key):
    if key == 'county':
        dir_path = 'counties'
    else:
        raise ValueError('not a valid key')
    dir_path = os.path.join('html_temp', dir_path)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    return dir_path

def get_html(state, script, div, the_type):

    """
    Create the HTML for each state
    """
    t = ENV.get_template('counties.j2')
    return t.render(state_name = state, 
            script =  script,
            div = div,
            the_type = the_type,
            )

def pre_graphs(state, df, sort_by = 'adjusted'):
    counties = list(set(df[(df['state'] == state) ]['county'].tolist()))
    min_date = datetime.datetime(2100, 1, 1)
    max_date = datetime.datetime(1900, 1, 1)
    max_y = 0
    ranks = []
    for i in counties:
        df_c = df[(df['state'] == state) & (df['county'] == i)]
        by_pop = df_c['new_deaths']/df_c['population'] * 1e6
        pop = df_c['new_deaths']
        m = round(by_pop.mean(),1)
        l = [x for x in by_pop if x != 0 ]
        r = round(len(l)/len(by_pop),2)
        if m == 0 or r <= .1:
            continue
        y = by_pop.rolling(7).mean()
        dates = df_c['date']
        if min(dates)< min_date:
            min_date = min(dates)
        if max(dates) > max_date:
            max_date = max(dates)
        if max([x for x in y.tolist() if not np.isnan(x)]) > max_y:
            max_y =  max([x for x in y.tolist() if not np.isnan(x)])
        if sort_by == 'adjusted':
            ranks.append((i, sum([x for x in y.tolist() if not np.isnan(x)])))
        else:
            ranks.append((i, sum([x for x in pop.tolist() if not np.isnan(x)])))
    return ranks, min_date, max_date, max_y

def state_counties(df, state):
    ps = []
    ranks, min_date, max_date, max_y = pre_graphs(state, df)
    ranks = sorted(ranks, key = lambda x: x[1], reverse = True)
    for i in [x[0] for x in ranks]:
        df_c = df[(df['state'] == state) & (df['county'] == i)]
        by_pop = df_c['new_deaths']/df_c['population'] * 1e6
        y = by_pop.rolling(7).mean()
        dates = df_c['date']
        p = figure(x_axis_type = 'datetime', plot_width = 250, plot_height = 250,
                  title = '{i}'.format(i =i), y_range = (0,max_y),
                  x_range = (min_date, max_date))
        p.vbar(x=dates, top=y) 
        p.yaxis.axis_label = 'deaths/million'
        ps.append(p)
    grid = gridplot(ps, ncols = 4)
    return grid

def do_counties():
    df = get_county_data()
    states = set(df['state'])
    for state in states:
        the_type = 'deaths'
        grid = state_counties(df, state)
        script, div = components(grid)
        html = get_html(state = state, script = script, div = div, the_type = 'Deaths')
        dir_path = make_counties_dir('county')
        with open(os.path.join(dir_path, 
                '{state}_{the_type}'.format(state = common.make_hyphenated(state),
                    the_type = the_type)), 'w') as write_obj:
             write_obj.write(html)

if __name__ == '__main__':
    do_counties()
