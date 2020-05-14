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

def get_data_cases():
    sql = """
    /* STATE CASES */
    select * from 
    (
    select DATE_TRUNC(date, week) as date,
state,
county,
sum(cases) as cases, 
the_rank
from
(
SELECT c.date,
c.state,
case when the_rank <= 3 then c.county else 'other' end as county,
c.new_cases as cases,
the_rank
FROM `paul-henry-tremblay.covid19.us_counties_diff` c
inner join covid19.cases_ranked_by_county r
on r.state = c.state
and r.county = c.county
)
group by date_trunc(date, week), county, state, the_rank
) order by date
    """
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    final = []
    D = {'date':[],
            'state':[],
            'county':[],
            'cases':[],
            'the_rank': [],
            }
    for i in result:
        D['date'].append(i.get('date'))
        D['state'].append(i.get('state'))
        D['county'].append(i.get('county'))
        D['cases'].append(i.get('cases'))
        D['the_rank'].append(i.get('the_rank'))
        final.append([i.get('date'),  i.get('state'),  i.get('county'), i.get('cases'), i.get('the_rank') ])
    pp.pprint(D)
    assert False
    d = {}
    d['dates'] = [x[0] for x in final]
    d['state'] = [x[1] for x in final]
    d['county'] = [x[2] for x in final]
    d['cases'] = [x[3] for x in final]
    d['rank'] = [x[4] for x in final]
    df = pd.DataFrame.from_dict(d)
    return df

def get_data_deaths():
    sql = """
    /* STATE DEATHS */
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
    dates = df_['dates'].tolist()
    temp_dict = dict(zip(dates, deaths))
    final = []
    for i in the_dict['dates']:
        final.append(temp_dict.get(i, 0))
    the_dict[county_name]= final

def get_html(date, territory, script, div):
    """
    Create the HTML for each state
    """
    t = ENV.get_template('countries.html')
    return t.render(title = territory, 
            script =  script,
            date = date,
            div = div
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

def _trim_data(d, start = 0):
    d_ = {}
    for i in d.keys():
        d_[i] = d[i][start:-1]
    return d_

def make_state_graphs():
    df = get_data_cases()

def _make_state_graphs():
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    date = datetime.datetime.now()
    df = get_data_deaths()
    dir_path = make_territories_dir('state')
    the_dict = {'dates': sorted(list(set(df['dates'].tolist())))}
    for state in ['Washington']:
        for i in range(1,5):
            shape_data(df, state, i, the_dict, key = 'death')
        the_dict = _trim_data(the_dict)
        p_deaths_stacked = common.graph_stacked(data = the_dict, start = 0, 
                plot_height = 450,line_width = 10)
        grid = gridplot([p_deaths_stacked], ncols = 2)
        script, div = components(grid)
        html = get_html(territory = state, script = script, div = div,
                date = date,
                    )
        tt = '{territory}'.format(territory = common.tidy_name(state)) + '_.html'
        with open(os.path.join(dir_path, tt), 'w') as write_obj:
            write_obj.write(html)

if __name__ == '__main__':
    make_state_graphs()
