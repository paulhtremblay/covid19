import os
import datetime
from google.cloud import bigquery
import pandas as pd
import math
import pprint
import csv
from henry_covid19 import variables
pp = pprint.PrettyPrinter(indent = 4)

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

from jinja2 import Environment, select_autoescape, FileSystemLoader

from slugify import slugify

from henry_covid19 import common
from henry_covid19.states_data import us_states_list as states_list

DIR = os.path.split(os.path.abspath(__file__))[0]

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

ENV.filters['slugify'] = slugify

def get_state_data(test = False):
  if test:
        return states_list
  sql = """
/* US STATES */
  SELECT date, state, new_cases as cases, new_deaths as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
order by date
  """
  client = bigquery.Client(project='paul-henry-tremblay')

  result = client.query(sql)
  final = []
  for i in result:
    date = i.get('date')
    cases = i.get('cases')
    final.append([date, i.get('state'), cases, i.get('deaths')])
  return final

def rates(df_states,  min_value, window = 3):
    states = sorted(set(df_states['state'].tolist()))
    l = []
    for i in states:
        increase_deaths = common.get_rate_increase(
               df = df_states[(df_states['state']==i) & (df_states['deaths'] > min_value)],
                key = 'deaths', window =window)
        increase_cases = common.get_rate_increase(
               df = df_states[(df_states['state']==i) & (df_states['cases'] > min_value)],
                key = 'cases', window =window)
        if len(increase_deaths) == 0 or len(increase_deaths) == 1 or math.isnan(increase_deaths[-1]):
            last_value_deaths = None
            double_r_deaths = None
        else:
            last_value_deaths = round(increase_deaths[-1],2)
            double_r_deaths  = common.get_double_rate(last_value_deaths)
        if len(increase_cases) == 0 or len(increase_cases) == 1 or math.isnan(increase_cases[-1]):
            last_value_cases = None
            double_r_cases = None
        else:
            last_value_cases= round(increase_cases[-1],2)
            double_r_cases  = common.get_double_rate(last_value_cases)
        l.append([i, last_value_deaths, double_r_deaths,
            last_value_cases, double_r_cases])
    l.insert(0, ['state', 'deaths_rate', 'deaths_double', 'cases_rate', 'cases_double'])
    with open('html_temp/rates.csv', 'w') as write_obj:
        writer = csv.writer(write_obj)
        writer.writerows(l)

def all_states(df_states, key, min_value, window = 3, 
        plot_height = 300, plot_width = 300):
    states = sorted(set(df_states['state'].tolist()))
    p_list = []
    for i in states:
        increase = common.get_rate_increase(
               df = df_states[(df_states['state']==i) & (df_states[key] > min_value)],
                key = key, window =window)
        if len(increase) == 0 or len(increase) == 1 or math.isnan(increase[-1]):
            continue
        min_val = increase[-1]
        if min_val < 1:
            n = common.get_days_less_than_0(increase)
            msg = 'under 1 for {n} days'.format(n = n)
        else:
            double_rate = common.get_double_rate(min_val)
            msg = 'doubles every {b} days'.format(b = round(double_rate))
        p = figure( plot_height = plot_height, plot_width = plot_width, 
                title = '{state}: {msg}'.format(
                    state = i, 
                    msg = msg
                    )
                )
        p.line(x = range(len(increase)), y = increase )
        p.line(x = range(len(increase)), y = [1 for x in increase], 
           line_dash = 'dashed', color = 'black')
        p_list.append(p)
    grid = gridplot(p_list, ncols = 4)
    return grid

def get_html(script, div, date, title, the_type ):
    """
    Create the HTML for each state
    """
    t = ENV.get_template('data.j2')
    if the_type == 'deaths':
        page_title = 'States Rate of Growth Deaths'
    elif the_type == 'cases':
        page_title = 'States Rate of Growth Infections'
    return t.render(page_title = page_title,
            script =  script,
            date = date,
            page_class_attr = ["infectionGrowthRate"],
            div = div,
            )

def make_rt_html(window = 3):
    window = int(variables.values['rt_window'])
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    df_states = common.make_dataframe(get_state_data(test = False))
    #make CSV
    rates(df_states,  min_value = 0, window = window)
    date = datetime.datetime.now()
    for i in [('deaths', 'states_deaths_rt', 'Death Rate', 'deaths', ), 
            ('cases', 'states_cases_rt', 'Cases Rate', 'cases')]:
        grid = all_states(df_states = df_states, key = i[0], min_value = 0, 
                window = window)
        script, div = components(grid)
        html = get_html(script, div, date, i[2], the_type = i[3])
        with open(os.path.join('html_temp', i[1]), 'w') as write_obj:
            write_obj.write(html)

if __name__ == '__main__':
    make_rt_html()
