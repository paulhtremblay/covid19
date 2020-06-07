import datetime
import math
import os
import pprint
pp = pprint.PrettyPrinter(indent = 4)
from google.cloud import bigquery
import pandas as pd
import numpy as np
import csv
from slugify import slugify

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

from jinja2 import Environment, select_autoescape, FileSystemLoader

from henry_covid19 import common
from henry_covid19 import variables
from henry_covid19 import bootstrap

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

def get_state_pop():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states_population.csv')
    d = {}
    with open(path, 'r') as read_obj:
        reader = csv.DictReader(read_obj)
        for row in reader:
            d[row['state']] = int(row['population_2019'])
    return d

def get_state_data_day():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_data_cases():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states_cases_ranked.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_data_deaths():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states_deaths_ranked.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    return df

def shape_data(df, state, rank, the_dict, key):
    start = 1
    if rank == 4:
        df_ = df[(df['state']==state) & (df['county'] == 'other')]
    else:
        df_ = df[(df['state']==state) & (df['rank'] == rank)]
    l = df_['county'].tolist()
    if len(l) == 0:
        return
    county_name = list(set(df_['county'].tolist()))[0]
    deaths = df_[key].tolist()
    dates = df_['date'].tolist()
    temp_dict = dict(zip(dates, deaths))
    final = []
    for i in the_dict['date']:
        final.append(temp_dict.get(i, 0))
    the_dict[county_name]= final

def get_html(date, territory, script, div, curr_death, last_week_deaths,
        p_curr_week, p_last_week, cur_week_per_million, last_week_per_million):

    """
    Create the HTML for each state
    """
    if cur_week_per_million == None:
        cur_week_per_million = ''
    else:
        cur_week_per_million = '({n} per million)'.format(n = cur_week_per_million)
    if last_week_per_million == None:
        last_week_per_million = ''
    else:
        last_week_per_million = '({n} per million)'.format(n = last_week_per_million)
    sig_curr = ''
    if p_curr_week > .1:
        sig_curr = '(not significant change from previous)'
    sig_prev = ''
    if p_last_week > .1:
        sig_prev = '(not significant change from previous)'
    t = ENV.get_template('countries.j2')
    return t.render(page_title = territory,
            script =  script,
            date = date,
            page_class_attr = ["state", "graph", slugify(territory)],
            div = div,
            curr_death = int(round(curr_death)),
            last_week_deaths = int(round(last_week_deaths)),
            sig_curr = sig_curr,
            sig_prev = sig_prev,
            cur_week_per_million = cur_week_per_million,
            last_week_per_million = last_week_per_million,
            )

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

def _trim_data(d):
    d_ = {}
    start = math.inf
    for i in d.keys():
        if i == 'date':
            continue
        for counter, j in enumerate(d[i]):
            if j > 0 and counter < start:
                start = counter
    for i in d.keys():
        d_[i] = d[i][start:-1]
    return d_

def _make_state_graphs(verbose = False):
    df_day = get_state_data_day()
    for state in ['Washington']:
        for the_info in [(None, 'deaths', df_day, 'deaths'), (None, 'cases', df_day, 'cases')]:
            df_day_ = the_info[2]
            p = common.incidents_over_time_bar(df_day_[df_day_['state'] == state ], 
                    key = the_info[3], window= 3, plot_height = 350, 
                plot_width = 350, title = 'Deaths by Day', line_width = 2)

def make_territories_ref_list(territory_key, territories):
    """
    create the link page  for each state
    """
    territories = sorted(territories)
    d = {'country': 'countries', 'state': 'states'}
    if territory_key == 'state':
        path = 'states/index.html'
        page_title = 'States'
    else:
        path = 'countries/index.html'
        page_title = 'Countries'
    t = ENV.get_template('territories_ref.j2')
    t =  t.render(page_title = page_title,
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            page_class_attr = ["regionList", territory_key.lower()],
            territories = [(slugify(x), x) for x in territories]
            )
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    with open(os.path.join('html_temp', path), 'w') as write_obj:
        write_obj.write(t)

def _get_first_nonzero(x):
    for counter, i in enumerate(x):
        if i != 0 and not np.isnan(i):
            return counter
    return 0

def _get_stats_for_state(deaths, pop):
    current_week = deaths[-7:]
    last_week = deaths[-14:-7]
    last_week_2 = deaths[-21:-14]
    the_dict = {}
    resample1, resample2 = bootstrap.resample_two_samples(last_week, current_week, num_iterations = 1000)
    both = bootstrap.combine_resamples(last_week, current_week, resample1, resample2)
    p_value = bootstrap.get_p_value(both)

    resample3, resample4 = bootstrap.resample_two_samples(last_week_2, last_week, num_iterations = 1000)
    both2 = bootstrap.combine_resamples(last_week_2, current_week, resample3, resample4)
    p_value2 = bootstrap.get_p_value(both2)

    the_dict['p_value_last_week'] =  p_value
    the_dict['p_value_last_week2'] =  p_value2
    the_dict['current_week_mean'] = np.mean(current_week)
    the_dict['last_week_mean'] = np.mean(last_week)
    the_dict['last_week_mean_2'] = np.mean(last_week_2)
    if pop == None:
        the_dict['current_week_per_million'] = None
        the_dict['last_week_per_million'] = None
    else:
        the_dict['current_week_per_million'] = round(float(np.mean(current_week))/pop * 1000000, 1)
        the_dict['last_week_per_million'] = round(float(np.mean(last_week))/pop * 1000000, 1)
    return the_dict

def change_with_sig(df, state_pop):
    the_dict = {}
    for i in list(set(df['state'])):
        df_ = df[df['state'] == i]
        deaths = df_['deaths'].tolist()
        the_dict[i] = _get_stats_for_state(deaths, state_pop.get(i, None))
    return the_dict

def make_wa():
    dir_path = make_territories_dir('state')
    t = ENV.get_template('wa.j2')
    html =  t.render(state_name = 'Washington',
            the_type = 'Deaths'
            )
    with open(os.path.join(dir_path, 'wa'), 'w') as write_obj:
            write_obj.write(html)

def make_state_graphs(verbose = False, plot_height = 400, plot_width = 400, 
        window = None):
    state_pop = get_state_pop()
    if not window:
        window = int(variables.values['by_state_window'])
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    df_day = get_state_data_day()
    change_dict = change_with_sig(df_day, state_pop)
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df_deaths = get_data_deaths()
    df_cases = get_data_cases()
    df_day = get_state_data_day()
    dir_path = make_territories_dir('state')
    for state in set(df_deaths['state']):
        if verbose:
            print('working on {state}'.format(state = state))
        ps = []
        for the_info in [
                (df_deaths, 'deaths', df_day, 'deaths', 
                    'Deaths by Week'.format(w = window), 
                    'Deaths by Day ({w} day mean)'.format(w = window)), 
                (df_cases, 'cases', df_day, 'cases', 
                    'Cases by Week', 
                    'Cases by Day ({w} day mean)'.format(w = window))]:
            df = the_info[0]
            df_day_ = the_info[2]
            rt_death, rt_death2 = common.get_rt(df_day_[df_day_['state'] == state]['deaths'], 7, 7)
            rt_cases, rt_cases2 = common.get_rt(df_day_[df_day_['state'] == state]['cases'], 7, 7)
            the_dict = {'date': sorted(list(set(df['date'].tolist())))}
            for i in range(1,5):
                shape_data(df, state, i, the_dict, key = the_info[1], 
                        )
            the_dict = _trim_data(the_dict)
            y = df_day_[df_day_['state'] == state][the_info[1]].rolling(window).mean()  
            first = _get_first_nonzero(y)
            y = y[first:]
            x = df_day_[df_day_['state'] == state]['date'] 
            x = x[first:]
            p = common.graph_stacked(data = the_dict, start = 0, 
                    plot_height = plot_height,plot_width = plot_width ,
                    line_width = 10, title = the_info[4] )
            p_day = common.incidents_over_time_bar2(
                    x = x,
                    y = y,  
                    plot_height = plot_height, 
                    line_width = 3,
                    plot_width = plot_width, title = the_info[5])
            ps.append(p)
            ps.append(p_day)
        grid = gridplot(ps, ncols = 2)
        script, div = components(grid)
        html = get_html(territory = state, script = script, div = div,
                date = date, 
                last_week_deaths = change_dict[state]['last_week_mean'],
                curr_death = change_dict[state]['current_week_mean'],
                p_curr_week = change_dict[state]['p_value_last_week'],
                p_last_week = change_dict[state]['p_value_last_week2'],
                cur_week_per_million = change_dict[state]['current_week_per_million'],
                last_week_per_million = change_dict[state]['last_week_per_million'],
                    )
        with open(os.path.join(dir_path, 
            '{territory}'.format(territory = slugify(state))), 'w') as write_obj:
            write_obj.write(html)
    make_territories_ref_list('state', list(set(df_day['state'])))
    make_wa()

if __name__ == '__main__':
    make_state_graphs()
