import math
import datetime
import os
from google.cloud import bigquery
import pandas as pd

from jinja2 import Environment, select_autoescape, FileSystemLoader

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components
from henry_covid19 import common

import pprint
pp = pprint.PrettyPrinter(indent = 4)


DIR = os.path.split(os.path.abspath(__file__))[0]

ENV = Environment(
    loader=FileSystemLoader(os.path.join(DIR, 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)


def get_world_data_week():
    """
    get the data from BQ, grouped by week
    """
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'world_week.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    df['dates'] = df['date']
    return df

def get_world_data_day():
    """
    Get the data by day for world

    return: df
    """
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'world.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    df['dates'] = df['date']
    return df



def get_html(territory, script, div, death_ro, death_double_rate, 
        cases_ro, cases_double_rate):
    """
    Create the HTML for each state
    """
    if death_ro == None:
        death_ro = 0
    if cases_ro == None:
        cases_ro = 0
    t = ENV.get_template('countries.j2')
    return t.render(title = territory, 
            script = script,
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            page_class_attr = ["country", "graph", common.make_hyphenated(territory)],
            death_ro = round(death_ro, 1), cases_ro = round(cases_ro,1),
            death_double_rate = death_double_rate, 
            cases_double_rate = cases_double_rate,
            div = div
            )

def dy_dx(territory_key, territory, df, window, key, plot_height, plot_width, min_value = 0):
    """
    Create a figure and metrics for the rate of increase or decrease
    """
    increase = common.get_rate_increase(
           df = df[(df[territory_key]==territory) & (df[key] > min_value)],
            key = key, window =window)
    if len(increase) == 0 or len(increase) == 1 or math.isnan(increase[-1]):
        return None, None, None
    last_val = increase[-1]
    double_rate = common.get_double_rate(last_val)
    if last_val < 1:
        n = common.get_days_less_than_0(increase)
        msg = 'under 1 for {n} days'.format(n = n)
    else:
        if double_rate > 14:
            msg = 'flat'
        else:
            msg = 'doubles every {b} days'.format(b = round(double_rate))
    p = figure( plot_height = plot_height, plot_width = plot_width, 
            title = '{key}: {msg}'.format(
                msg = msg,
                key = key,
                )
            )
    p.line(x = range(len(increase)), y = increase )
    p.line(x = range(len(increase)), y = [1 for x in increase], 
       line_dash = 'dashed', color = 'black')
    return last_val, double_rate, p


def make_state_ref(states):
    """
    make the link to each state
    """
    s = ''
    for i in sorted(states):
        s += '<p><a href="{r}">{i}</a></p>\n'.format(
                i = i,
                r = 'states/' + i.replace(' ', '-').lower(),
                )
    return s

def make_territories_dir(key):
    if key == 'country':
        dir_path = 'countries'
    elif key == 'state':
        dir_path = 'states'
    else:
        raise ValueError('not a valid key')
    dir_path = os.path.join('html_temp', dir_path)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
    return dir_path

def make_territories_ref_list(territory_key, territories):
    """
    create the link page  for each state
    """
    territories = sorted(territories)
    d = {'country': 'countries', 'state': 'states'}
    if territory_key == 'state':
        path = 'states_list'
        page_title = 'States'
    else:
        path = 'countries_list'
        page_title = 'Countries'
    t = ENV.get_template('territories_ref.j2')
    t =  t.render(title = 'By {k}'.format(k = territory_key), 
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            page_title = page_title,
            page_class_attr = ["regionList", territory_key.lower()],
            territories = [(common.make_hyphenated(x), x) for x in territories]
            )
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    with open(os.path.join('html_temp', path), 'w') as write_obj:
        write_obj.write(t)

def all_territories(df_week, df_day, territory_key, window = 3, plot_height = 550,
        plot_width = 550, verbose = False):
    """
    Create all the HTML files for the states
    """
    territories = list(set(df_week[territory_key]))
    make_territories_ref_list(territory_key, territories)
    dir_path = make_territories_dir(territory_key)
    for i in territories:
        if verbose:
            print('working on {territory}'.format(territory = i))
        min_value = 10
        df_ = df_week[(df_week[territory_key]==i)]
        p1 = common.bar_over_time(df_, key = 'deaths', 
                plot_height = plot_height, plot_width = plot_width, 
                title = 'Deaths by Week', line_width = 10, ignore_last = True)
        p6 = common.bar_over_time(df_, key = 'cases', 
                plot_height = plot_height, plot_width = plot_width, 
                title = 'Cases by Week', line_width = 10, ignore_last = True)
        p2 = common.incidents_over_time_bar(df_day[df_day[territory_key] == i], 
                key = 'deaths', window= 3, plot_height = plot_height, 
            plot_width = plot_width, title = 'Deaths by Day', line_width = 2)
        p5 = common.incidents_over_time_bar(df_day[df_day[territory_key] == i], 
                key = 'cases', window= 3, plot_height = plot_height, 
            plot_width = plot_width, title = 'Cases by Day', line_width = 2)
        death_ro, death_double_rate, p3 =  dy_dx(territory_key = territory_key, 
                territory = i, df = df_day, window = window, 
                key = 'deaths', plot_height = 300, plot_width = 300)
        cases_ro, cases_double_rate, p4 =  dy_dx(territory_key = territory_key, 
                territory = i, df = df_day, window = window, 
                key = 'cases', plot_height = 300, plot_width = 300)
        grid = gridplot([p1, p2, p6, p5,  p3, p4], ncols = 2)
        script, div = components(grid)
        html = get_html(territory = i, script = script, div = div,
                death_ro = death_ro, cases_ro = cases_ro, 
                death_double_rate = death_double_rate, 
                cases_double_rate = cases_double_rate)
        with open(os.path.join(dir_path, '{territory}'.format(
            territory = common.make_hyphenated(i))), 'w') as write_obj:
            write_obj.write(html)


def main():
    df_world_week = get_world_data_week()
    df_world_day = get_world_data_day()
    all_territories(df_week =  df_world_week, df_day = df_world_day, 
            territory_key = 'country', verbose = False)

if __name__ == '__main__':
    main()
