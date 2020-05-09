import os
import datetime
import pprint
pp = pprint.PrettyPrinter(indent = 4)
from google.cloud import bigquery
import pandas as pd

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import NumeralTickFormatter
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components

from jinja2 import Environment, select_autoescape, FileSystemLoader

from henry_covid19 import common

DIR = os.path.split(os.path.abspath(__file__))[0]

ENV = Environment(
    loader=FileSystemLoader(os.path.join(DIR, 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

"""
makes graphs for rates of states compared to US
logarithmic graphs
"""

def get_state_data():
    sql = """
    /* US STATES */
    SELECT date, state, cases, deaths FROM `paul-henry-tremblay.covid19.us_states`
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
    sql = """
    /* US */
    SELECT date, sum(cases) as cases, sum(deaths) as deaths 
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

def get_html(script, div):
    """
    Create the HTML
    """
    t = ENV.get_template('us_rates.html')
    return t.render(title = 'Rates', 
            script =  script,
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            div = div
            )
def main():
    df_states = common.make_dataframe(get_state_data())
    df_us = common.make_dataframe(get_us_data(), us= True)
    grid = all_states(df_states, df_us)
    script, div = components(grid)
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    html = get_html(script, div)
    with open('html_temp/states_deaths.html', 'w') as write_obj:
        write_obj.write(html)

if __name__ == '__main__':
    main()
