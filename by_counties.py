import datetime
import os
import shutil

import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.embed import components

from henry_covid19 import common
from henry_covid19 import variables

from slugify import slugify

from jinja2 import Environment, select_autoescape, FileSystemLoader

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
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
    if  os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)
    return dir_path

def make_county_ref_list(states):
    """
    create the link page  for each state
    """
    states = sorted(states)
    path = 'counties/index.html'
    page_title = 'Counties'
    t = ENV.get_template('counties_ref.j2')
    t =  t.render(title = 'By County',
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            page_title = page_title,
            page_class_attr = ["regionList", "state", "county"],
            territories = [(slugify(x), x) for x in states]
            )
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    with open(os.path.join('html_temp', path), 'w') as write_obj:
        write_obj.write(t)

def get_html(state, script, div, the_type):
    """
    Create the HTML for each state
    """
    if the_type == 'Deaths':
        link_name = 'Cases'
        link = '{state}-{the_type}'.format(state = slugify(state), the_type = 'cases')
    else:
        link_name = 'Deaths'
        link = '{state}-{the_type}'.format(state = slugify(state), the_type = 'deaths')
    t = ENV.get_template('counties.j2')
    return t.render(page_title = state + " " + the_type,
            script =  script,
            div = div,
            link = link,
            link_name = link_name,
            )

def pre_graphs(state, df, sort_by = 'adjusted', key = 'new_deaths'):
    counties = list(set(df[(df['state'] == state) ]['county'].tolist()))
    min_date = datetime.datetime(2100, 1, 1)
    max_date = datetime.datetime(1900, 1, 1)
    max_y = 0
    ranks = []
    for i in counties:
        df_c = df[(df['state'] == state) & (df['county'] == i)]
        by_pop = df_c[key]/df_c['population'] * 1e6
        pop = df_c[key]
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
        try:
            if max([x for x in y.tolist() if not np.isnan(x)]) > max_y:
                max_y =  max([x for x in y.tolist() if not np.isnan(x)])
        except ValueError:
            continue
        if sort_by == 'adjusted':
            ranks.append((i, sum([x for x in y.tolist() if not np.isnan(x)])))
        else:
            ranks.append((i, sum([x for x in pop.tolist() if not np.isnan(x)])))
    return ranks, min_date, max_date, max_y

def state_counties(df, state, key = 'new_deaths'):
    ps = []
    ranks, min_date, max_date, max_y = pre_graphs(state, df, key = key)
    ranks = sorted(ranks, key = lambda x: x[1], reverse = True)
    for i in [x[0] for x in ranks]:
        df_c = df[(df['state'] == state) & (df['county'] == i)]
        by_pop = df_c[key]/df_c['population'] * 1e6
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
    title = {'deaths':'Deaths', 'cases': 'Cases'}
    keys = {'deaths': 'new_deaths', 'cases':'new_cases'}
    dir_path = make_counties_dir('county')
    for the_type in ['deaths', 'cases']:
        for state in states:
            grid = state_counties(df, state, key=keys[the_type])
            script, div = components(grid)
            html = get_html(state=state, script=script, div=div, the_type=title[the_type])
            with open(os.path.join(dir_path,
                    '{state}-{the_type}'.format(state=common.slugify(state),
                    the_type=the_type)), 'w') as write_obj:
                write_obj.write(html)
    make_county_ref_list(states)

if __name__ == '__main__':
    do_counties()
