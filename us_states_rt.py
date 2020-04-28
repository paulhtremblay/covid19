from google.cloud import bigquery
import pandas as pd
import math
import pprint
import csv
pp = pprint.PrettyPrinter(indent = 4)

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

from henry_covid19 import common
from henry_covid19.states_data import us_states_list as states_list

def get_state_data(test = False):
  if test:
        return states_list
  sql = """SELECT date, state, cases, deaths FROM `paul-henry-tremblay.covid19.us_states`
order by date

  """
  client = bigquery.Client(project='paul-henry-tremblay')

  result = client.query(sql)
  final = []
  for i in result:
    date = i.get('date')
    cases = i.get('cases')
    final.append([date, i.get('state'), cases, i.get('deaths')])
  pp.pprint(final)
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
    with open('html_dir/rates.csv', 'w') as write_obj:
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
        if len(increase) == 0:
            continue
        if len(increase) == 1:
            continue
        if math.isnan(increase[-1]):
            continue
        min_val = common.get_double_rate(increase[-1])
        p = figure( plot_height = plot_height, plot_width = plot_width, 
                title = '{state}: doubles every {b} days'.format(
                    state = i, 
                    b = round(min_val)
                    )
                )
        #p.y_range.start = 0
        seven_day = math.pow(2, 1/7)
        p.line(x = range(len(increase)), y = increase )
        #p.line(x = [0, max(range(len(increase)))], y = [seven_day, seven_day])
        #p.line(x = [0, max(range(len(increase)))], 
        #y = [increase[-1], increase[-1]], legend_label = str(min_val))
        p_list.append(p)
    grid = gridplot(p_list, ncols = 4)
    return grid

def main():
    df_states = common.make_dataframe(get_state_data(test = False))
    rates(df_states,  min_value = 3, window = 3)
    grid = all_states(df_states = df_states, key = 'deaths', min_value = 10, 
            window = 3)
    grid2 = all_states(df_states = df_states, key = 'cases', min_value = 10, 
            window = 3)
    script, div = components(grid)
    script2, div2 = components(grid2)
    with open('html_dir/states_rt1.js', 'w') as write_obj:
        write_obj.write(script)
    with open('html_dir/states_rt1.div', 'w') as write_obj:
        write_obj.write(div)
    with open('html_dir/states_rt2.js', 'w') as write_obj:
        write_obj.write(script2)
    with open('html_dir/states_rt2.div', 'w') as write_obj:
        write_obj.write(div2)

if __name__ == '__main__':
    main()
