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

def graph_stacked(data, start = 3, plot_height = 450,line_width = 10):
    labels = list(data.keys())
    del(labels[labels.index('dates')])
    colors = ['blue', 'green', 'red', 'orange']
    colors = colors[0:len(labels) ]
    p = figure( plot_height=plot_height, title="Covid19 Deaths Washington",
           x_axis_type= 'datetime')

    r = p.vbar_stack(labels, x='dates', width=1, color=colors, source=data,
             legend_label=labels, line_width = line_width)

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "vertical"
    p.legend.glyph_height = 1
    p.legend.glyph_width= 1
    p.legend.spacing  = 30
    p.legend.label_standoff = 30
    return p


def make_state_graphs():
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    date = datetime.datetime.now()
    dates = [datetime.datetime(2020, 1, 1), 
            datetime.datetime(2020, 1, 7),
            datetime.datetime(2020, 1, 14),
            datetime.datetime(2020, 1, 21),
            datetime.datetime(2020, 1, 28),
            datetime.datetime(2020, 2, 7),
            ]
    """
    p =graph_stacked(  data = {'dates': dates,
                'first': [1, 2, 3, 4, 5, 6], 
            'second': [1, 2, 3, 4, 5, 6], 
            'third': [1, 2, 3, 4, 5, 6], 
            })
    p =graph_stacked(  data = {'dates': dates,
                'first': [1, 2, 3, 4, 5, 6], 
            'second': [1, 2, 3, 4, 5, 6], 
            })
    """
    #show(p)
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
        the_dict[county_name]= deaths
    the_dict = {}
    for i in range(1,5):
        get_key(df, 'Washington', i, the_dict)
    the_dict['dates'] = df[(df['state']=='Washington') & (df['rank'] == 1)]['dates'].tolist()
    p = graph_stacked(data = the_dict, start = 0, plot_height = 450,line_width = 10)
    #show(p)

if __name__ == '__main__':
    make_state_graphs()
