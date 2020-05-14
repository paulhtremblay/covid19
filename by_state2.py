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

def get_data():
    sql = """
    select * from 
    (
    select DATE_TRUNC(date, week) as date,
state,
county,
sum(deaths) as deaths, 
the_rank
from
(
SELECT c.date,
c.state,
case when the_rank <= 3 then c.county else 'other' end as county,
c.new_deaths as deaths,
the_rank
FROM `paul-henry-tremblay.covid19.us_counties_diff` c
inner join covid19.deaths_ranked_by_county r
on r.state = c.state
and r.county = c.county
)
group by date_trunc(date, week), county, state, the_rank
) order by date
    """
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    final = []
    for i in result:
        final.append([i.get('date'),  i.get('state'),  i.get('county'), i.get('deaths'), i.get('the_rank') ])
    d = {}
    d['dates'] = [x[0] for x in final]
    d['state'] = [x[1] for x in final]
    d['county'] = [x[2] for x in final]
    d['death'] = [x[3] for x in final]
    d['rank'] = [x[4] for x in final]
    df = pd.DataFrame.from_dict(d)
    return df

def make_state_graphs():
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    date = datetime.datetime.now()
    df = get_data()
    def get_key(df, state, rank, the_dict):
        if rank == 4:
            df_ = df[(df['state']==state) & (df['county'] == 'other')]
        else:
            df_ = df[(df['state']==state) & (df['rank'] == rank)]
        l = df_['county'].tolist()
        if len(l) == 0:
            return
        county_name = list(set(df_['county'].tolist()))[0]
        deaths = df_['death'].tolist()
        dates = df_['dates'].tolist()
        temp_dict = dict(zip(dates, deaths))
        final = []
        for i in the_dict['dates']:
            final.append(temp_dict.get(i, 0))
        the_dict[county_name]= final
    the_dict = {}
    the_dict['dates'] = sorted(list(set(df['dates'].tolist())))
    for i in range(1,5):
        get_key(df, 'Washington', i, the_dict)
    the_dict['dates'] = [datetime.datetime(x.year, x.month, x.day) for x in the_dict['dates']]
    p = common.graph_stacked(data = the_dict, start = 0, plot_height = 450,line_width = 10)
    show(p)

if __name__ == '__main__':
    make_state_graphs()
