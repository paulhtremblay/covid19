import datetime
import math
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

def get_state_data_day():
    """
    Get the data by day for US states

    return: a list
    """
    sql = """
    /* STATE BY DAY */
  SELECT  date, state, new_cases as cases, new_deaths as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
order by date
  """
    client = bigquery.Client(project='paul-henry-tremblay')

    result = client.query(sql)
    l = []
    for i in result:
        date = i.get('date')
        cases = i.get('cases')
        l.append([date, i.get('state'), cases, i.get('deaths')])
    d = {}
    d['dates'] = [x[0] for x in l]
    d['state'] = [x[1] for x in l]
    d['cases'] = [x[2] for x in l]
    d['deaths'] = [x[3] for x in l]
    df = pd.DataFrame.from_dict(d)
    return df

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
    for i in result:
        final.append([i.get('date'),  i.get('state'),  i.get('county'), i.get('cases'), i.get('the_rank') ])
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

def _trim_data(d):
    d_ = {}
    start = math.inf
    for i in d.keys():
        if i == 'dates':
            continue
        for counter, j in enumerate(d[i]):
            if j > 0 and counter < start:
                start = counter
    for i in d.keys():
        d_[i] = d[i][start:-1]
    return d_

def _make_state_graphs(verbose = False):
    df_day = get_state_data_day()
    for state in ['Washington']:
        for the_info in [(None, 'death', df_day, 'deaths'), (None, 'cases', df_day, 'cases')]:
            df_day_ = the_info[2]
            p = common.incidents_over_time_bar(df_day_[df_day_['state'] == state ], 
                    key = the_info[3], window= 3, plot_height = 350, 
                plot_width = 350, title = 'Deaths by Day', line_width = 2)

def make_state_graphs(verbose = False, plot_height = 400, plot_width = 400):
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    date = datetime.datetime.now()
    df_deaths = get_data_deaths()
    df_cases = get_data_cases()
    df_day = get_state_data_day()
    dir_path = make_territories_dir('state')
    for state in set(df_deaths['state']):
        if verbose:
            print('working on {state}'.format(state = state))
        ps = []
        for the_info in [
                (df_deaths, 'death', df_day, 'deaths', 'Deaths by Week', 'Deaths by Day',), 
                (df_cases, 'cases', df_day, 'cases', 'Cases by Week', 'Cases by Day')]:
            df = the_info[0]
            df_day_ = the_info[2]
            the_dict = {'dates': sorted(list(set(df['dates'].tolist())))}
            for i in range(1,5):
                shape_data(df, state, i, the_dict, key = the_info[1], 
                        )
            the_dict = _trim_data(the_dict)
            p = common.graph_stacked(data = the_dict, start = 0, 
                    plot_height = plot_height,plot_width = plot_width ,
                    line_width = 10, title = the_info[4])
            p_day = common.incidents_over_time_bar(df_day_[df_day_['state'] == state ], 
                    key = the_info[3], window= 3, plot_height = plot_height, 
                plot_width = plot_width, title = the_info[5], line_width = 2)
            ps.append(p)
            ps.append(p_day)
        grid = gridplot(ps, ncols = 2)
        script, div = components(grid)
        html = get_html(territory = state, script = script, div = div,
                date = date,
                    )
        tt = '{territory}'.format(territory = common.tidy_name(state)) + '.html'
        with open(os.path.join(dir_path, tt), 'w') as write_obj:
            write_obj.write(html)

if __name__ == '__main__':
    make_state_graphs()
