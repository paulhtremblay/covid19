import datetime
import os
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

ENV = Environment(
    loader=FileSystemLoader(os.path.join(
        os.path.split(os.path.abspath(__file__))[0], 
        'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

"""
makes bar graphs for deaths/cases for WA and by counties
"""

def get_data_wash_order_county():
    sql = """
    /* WA COUNTIES */
  with t1  as
(
SELECT DATE_TRUNC(date, week) as date,
sum(king) as king,
sum( snohomish) as  snohomish,
sum(other) as other
from(
SELECT date,
sum(case when county = 'King' then new_deaths else 0 end) as king,
sum(case when county = 'Snohomish' then new_deaths else 0 end) as snohomish,
sum(case when county not in ('King', 'Snohomish') then new_deaths else 0 end) as other
FROM `paul-henry-tremblay.covid19.us_counties_diff`
where state = 'Washington'
group by date
)
group by DATE_TRUNC(date, week)
)
select * from t1 order by date
  """
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    final = []
    for i in result:
        final.append([i.get('date'),  i.get('king'),  i.get('snohomish'), i.get('other')])
    return final

def make_dataframe_wash_order():
  l = get_data_wash_order_county()
  d = {}
  d['dates'] = [x[0] for x in l]
  d['king'] = [x[1] for x in l]
  d['snohomish'] = [x[2] for x in l]
  d['other'] = [x[3] for x in l]

  df = pd.DataFrame.from_dict(d)
  return df

def get_state_data():
    sql = """
    /* 'US STATES' */
  SELECT  date, state, new_cases as cases, new_deaths as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
order by date
  """
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    final = []
    for i in result:
        final.append([i.get('date'), i.get('state'), i.get('cases'), i.get('deaths')])
    return final

def get_html(script, div, date, title):
    """
    Create the HTML for each state
    """
    t = ENV.get_template('data.html')
    return t.render(title = title, 
            script =  script,
            date = date,
            site_name = 'Covid 19 Data: Cases, Deaths, and Changes by State',
            div = div,
            page_title = 'States Rate of Growth Deaths',
            )

def make_washington_graphs():
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    date = datetime.datetime.now()
    df_states = common.make_dataframe(get_state_data())
    df_counties =  make_dataframe_wash_order()
    p_counties = common.graph_wash_county_order(df = df_counties, 
            start = 3, plot_height = 450, line_width = 40)
    df_state = df_states[(df_states['state']=='Washington')]
    p_all = common.incidents_over_time_bar(df_state, key = 'deaths', 
            window= 3, plot_height = 600, 
            plot_width = 600, title = None)
    grid = gridplot([p_all, p_counties], ncols = 4)
    script, div = components(grid)
    html = get_html(script, div, date, title = 'Washington')
    with open('html_temp/wa.html', 'w') as write_obj:
        write_obj.write(html)

if __name__ == '__main__':
    make_washington_graphs()
