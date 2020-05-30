import datetime
import math
import os
import pprint
pp = pprint.PrettyPrinter(indent = 4)
from google.cloud import bigquery
import pandas as pd
import numpy as np
import csv


from jinja2 import Environment, select_autoescape, FileSystemLoader

from henry_covid19 import common
from henry_covid19 import variables
from henry_covid19 import bootstrap

ENV = Environment(
    loader=FileSystemLoader(os.path.join(
        os.path.split(os.path.abspath(__file__))[0], 
        'templates')),
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

def get_totals():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states_totals.csv')
    d = {}
    with open(path, 'r') as read_obj:
        reader = csv.DictReader(read_obj)
        for row in reader:
            d[row['state']] = {'deaths': int(row['deaths']), 'cases':int(row['deaths'])}
    return d

def _get_stats_for_state(deaths, cases, pop):
    current_week = deaths[-7:]
    last_week = deaths[-14:-7]
    last_week_2 = deaths[-21:-14]
    current_week_cases = cases[-7:]
    last_week_cases = cases[-14:-7]
    last_week_2_cases = cases[-21:-14]
    the_dict = {}
    for i in [
            (last_week, current_week, 'p_value_death_current_last'), 
            (last_week_2, current_week, 'p_value_death_last_last2'),
            (last_week_cases, current_week_cases, 'p_value_cases_current_last'), 
            (last_week_2_cases, current_week_cases, 'p_value_cases_last_last2'),
            ]:
        resample1, resample2 = bootstrap.resample_two_samples(i[0], i[1], num_iterations = 1000)
        both = bootstrap.combine_resamples(last_week, current_week, resample1, resample2)
        p_value = bootstrap.get_p_value(both)
        the_dict[i[2]] = p_value
    the_dict['current_week_mean'] = np.mean(current_week)
    the_dict['last_week_mean'] = np.mean(last_week)
    the_dict['last_week_mean_2'] = np.mean(last_week_2)
    the_dict['current_week_cases_mean'] = np.mean(current_week_cases)
    the_dict['last_week_cases_mean'] = np.mean(last_week_cases)
    the_dict['last_week_cases_mean_2'] = np.mean(last_week_2_cases)
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
        cases = df_['cases'].tolist()
        the_dict[i] = _get_stats_for_state(deaths, cases, state_pop.get(i, None))
    return the_dict

def get_state_data_day():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'states.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    return df

def make_state_tables(verbose = False, window = None):
    state_pop = get_state_pop()
    totals = get_totals()
    if not window:
        window = int(variables.values['by_state_window'])
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    df_day = get_state_data_day()
    for state in set(df_day['state']):
        if verbose:
            print('working on {state}'.format(state = state))
    change_dict = change_with_sig(df_day, state_pop)
    field_names = ['state', 
    'current_week_mean',
                   'current_week_per_million',
                   'last_week_mean',
                   'last_week_mean_2',
                   'last_week_per_million',
                   'last_week_cases_mean_2', 
                   'last_week_cases_mean', 
                   'current_week_cases_mean',
                   'p_value_cases_current_last',
                   'p_value_cases_last_last2',
                   'p_value_death_current_last',
                   'p_value_death_last_last2',
                   'total_cases', 
                   'total_deaths',
                   'total_cases_per_million', 
                   'total_deaths_per_million',
                   ]

    with open(os.path.join('data', 'data_table.csv'), 'w') as write_obj:
        csv_writer = csv.DictWriter(write_obj, fieldnames=field_names)
        csv_writer.writeheader()
        for state in sorted(change_dict.keys()):
            d = change_dict[state]
            d['state'] = state
            d['total_deaths'] = totals[state]['deaths']
            d['total_cases'] = totals[state]['cases']
            pop = state_pop.get(state)
            if pop == None:
                d['total_deaths_per_million'] = None
            else:
                d['total_deaths_per_million'] = (totals[state]['deaths']/pop) * 1e6
            if pop == None:
                d['total_cases_per_million'] = None
            else:
                d['total_cases_per_million'] = (totals[state]['cases']/pop) * 1e6
            csv_writer.writerow(d)


def get_html(header, body):
    t = ENV.get_template('data_table.j2')
    return t.render(table_head = header, 
            table_body =  body,
            )

def make_html_table(path):
    data = []
    header = None
    with open(os.path.join('data', 'data_table.csv'), 'r') as read_obj:
        counter = 0
        csv_reader = csv.DictReader(read_obj)
        print(csv_reader.fieldnames)
        for row in csv_reader:
            sig =  float(row['p_value_death_current_last']) <= .1
            if sig:
                sig = 'Yes'
            else:
                sig = 'No'
            try:
                deaths_mil = round(float(row['total_deaths_per_million']))
            except ValueError:
                deaths_mil = 0
            data.append([row['state'], 
                round(float(row['current_week_mean'])),
                row['current_week_per_million'],
                round(float(row['last_week_mean'])),
                row['last_week_per_million'],
                round(float(row['current_week_mean'])- float(row['last_week_mean'])),
                sig,
                row['total_deaths'],
                deaths_mil,
                ])
    header =['state', 'current week mean', 'per million', 'last week mean',
            'per million', 'change', 'significant', 'total_deaths', 'per million']
    html = get_html(header = header, 
            body =data           )
    with open(os.path.join('html_temp', 'table_data.html'), 'w') as write_obj:
        write_obj.write(html)


if __name__ == '__main__':
    #make_state_tables()
    make_html_table(os.path.join('data', 'data_table.csv'))
