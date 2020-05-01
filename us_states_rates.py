from google.cloud import bigquery
import pandas as pd

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

from henry_covid19 import common
"""
makes graphs for rates of states compared to US
"""

def get_state_data():
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
  return final

def get_us_data():
  sql = """SELECT date, sum(cases) as cases, sum(deaths) as deaths 
  FROM `paul-henry-tremblay.covid19.us_states`
  group by date
  order by date
  """
  client = bigquery.Client(project='paul-henry-tremblay')
  result = client.query(sql)
  final = []
  for i in result:
    date = i.get('date')
    cases = i.get('cases')
    final.append([date, cases, i.get('deaths')])
  return final

def make_state_graph(df_state, df_us, min_deaths, state, 
        plot_height = 300, plot_width = 300, key = 'deaths'):
    p = figure ( y_axis_type = 'log', title = '{state}'.format(state = state),
                plot_width=plot_width, plot_height=plot_height)
    df_state = df_state[(df_state['state']==state) & ( df_state[key] > min_deaths)]
    df_us = df_us[(df_us['deaths'] > min_deaths)]
    p.line(x= range(len(df_state[key].tolist())),  y=df_state[key].tolist(), color='green', 
           legend_label = state, line_width = 2)
    seven_day = common.double_rate_line(start = min_deaths, rate =  7, 
            the_len = len(df_us[key].tolist()))
    two_day = common.double_rate_line(start = min_deaths, rate =  3, 
            the_len = len(df_us['deaths'].tolist()))
    p.line(x= range(len(df_us[key].tolist())),  y=df_us[key].tolist(), color='gray',
           legend_label = 'US')

    p.line(x = range(len(df_us[key].tolist())), y = seven_day, legend_label = '7 days',
           line_dash = 'dashed')
    p.line(x = range(len(df_us[key].tolist())), y = two_day, legend_label = '3 days',
           line_dash = 'dashed')
    p.legend.location = 'top_left'
    return p

def all_states(df_state, df_us):
  states = sorted(set(df_state['state'].tolist()))
  p_list = []
  for i in states:
    p_list.append(make_state_graph(df_state = df_state, 
        df_us = df_us, min_deaths = 10, state = i, key = 'deaths'))
  grid = gridplot(p_list, ncols = 4)
  return grid

def main():
    df_states = common.make_dataframe(get_state_data())
    df_us = common.make_dataframe(get_us_data(), us= True)
    grid = all_states(df_states, df_us)
    script, div = components(grid)
    with open('html_temp/states1.js', 'w') as write_obj:
        write_obj.write(script)
    with open('html_temp/states1.div', 'w') as write_obj:
        write_obj.write(div)

if __name__ == '__main__':
    main()
