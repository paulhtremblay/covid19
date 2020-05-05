import math
import datetime
import os
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
makes all graphs for states
"""

def get_state_data_week():
    sql = """
  select *
from
(
SELECT DATE_TRUNC(date, week) as date,
state,
sum(new_cases) as cases,
sum(new_deaths) as deaths
from covid19.us_states_day_diff
group by date_trunc(date,week), state
) order by state, date
  """
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    l = [[i.get('date'), i.get('state'), i.get('cases'), i.get('deaths')] for i in result]
    d = {}
    d['dates'] = [x[0] for x in l]
    d['state'] = [x[1] for x in l]
    d['cases'] = [x[2] for x in l]
    d['deaths'] = [x[3] for x in l]
    df = pd.DataFrame.from_dict(d)
    return df

def get_state_data_day():
  sql = """
  SELECT  date, state, new_cases as cases, new_deaths as deaths
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

def get_html(state, script, div, death_ro, death_double_rate, 
        cases_ro, cases_double_rate):
    return """
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{title}</title>

	<script src="https://cdnjs.cloudflare.com/ajax/libs/bokeh/2.0.2/bokeh.min.js">
	</script>

        <!-- COPY/PASTE SCRIPT HERE -->

        {script}

    </head>
    <body>
    <h1>{title}</h1>
    <p>updated: {date}</p>
    <p><a href = "index.html">home</a></p>
    <p>Cases RO: {cases_ro} Deaths RO: {death_ro} <p>
        {div}
    </body>
</html>
""".format(
        title = state, 
        div = div,
        script = script,
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        death_ro = round(death_ro, 1), cases_ro = round(cases_ro,1),
        death_double_rate = death_double_rate, 
        cases_double_rate = cases_double_rate
        )

def dy_dx(state, df, window, key, plot_height, plot_width, min_value = 0):
    increase = common.get_rate_increase(
           df = df[(df['state']==state) & (df[key] > min_value)],
            key = key, window =window)
    if len(increase) == 0 or len(increase) == 1 or math.isnan(increase[-1]):
        return
    last_val = increase[-1]
    double_rate = common.get_double_rate(last_val)
    if last_val < 1:
        n = common.get_days_less_than_0(increase)
        msg = 'under 1 for {n} days'.format(n = n)
    else:
        if double_rate > 14:
            msg = 'flat'
        else:
            msg = 'doubles every {b} days'.format(b = round(double_rate))
    p = figure( plot_height = plot_height, plot_width = plot_width, 
            title = '{key}: {msg}'.format(
                state = state, 
                msg = msg,
                key = key,
                )
            )
    p.line(x = range(len(increase)), y = increase )
    p.line(x = range(len(increase)), y = [1 for x in increase], 
       line_dash = 'dashed', color = 'black')
    return last_val, double_rate, p

def all_states(df_week, df_day, window = 3, plot_height = 300,
        plot_width = 300):
    states = list(set(df_week['state']))
    for i in states:
        min_value = 10
        if i != 'Washington':
            continue
        df_ = df_week[(df_week['state']==i)]
        p1 = common.bar_over_time(df_, key = 'deaths', 
                plot_height = plot_height, plot_width = plot_width, 
                title = 'By Week', line_width = 10, ignore_last = True)
        p2 = common.incidents_over_time_bar(df_day[df_day['state'] == i], 
                key = 'deaths', window= 3, plot_height = plot_height, 
            plot_width = plot_width, title = 'By Day', line_width = 2)
        death_ro, death_double_rate, p3 =  dy_dx(state = i, df = df_day, window = window, 
                key = 'deaths', plot_height = plot_height, plot_width = plot_width)
        cases_ro, cases_double_rate, p4 =  dy_dx(state = i, df = df_day, window = window, 
                key = 'cases', plot_height = plot_height, plot_width = plot_width)
        grid = gridplot([p1, p2, p3, p4], ncols = 4)
        script, div = components(grid)
        html = get_html(state = i, script = script, div = div,
                death_ro = death_ro, cases_ro = cases_ro, 
                death_double_rate = death_double_rate, cases_double_rate = cases_double_rate)
        with open(os.path.join('html_temp', 'states', '{state}.html'.format(
            state = i.lower())), 'w') as write_obj:
            write_obj.write(html)


def main():
    df_states_week = get_state_data_week()
    df_states_day = common.make_dataframe(get_state_data_day())
    all_states(df_week =  df_states_week, df_day = df_states_day)

if __name__ == '__main__':
    main()
