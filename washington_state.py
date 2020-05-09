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

from henry_covid19 import common

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
    final_dict = {
            'date': [],
            'king': [],
            'snohomish': [],
            'other': [],
            }
    for i in result:
        final.append([i.get('date'),  i.get('king'),  i.get('snohomish'), i.get('other')])
        final_dict['date'].append(i.get('date'))
        final_dict['king'].append(i.get('king'))
        final_dict['snohomish'].append(i.get('snohomish'))
        final_dict['other'].append(i.get('other'))
    pp.pprint(final_dict)
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

def make_washington_graphs():
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
    with open('html_temp/deaths_wa.js', 'w') as write_obj:
        write_obj.write(script)
    with open('html_temp/deaths_wa.div', 'w') as write_obj:
        write_obj.write(div)

if __name__ == '__main__':
    make_washington_graphs()
