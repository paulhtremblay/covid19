import datetime
import math
import os
import pathlib
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

from slugify import slugify

from henry_covid19 import common

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

ENV.filters['slugify'] = slugify

def get_data():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'sweden_vs.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    return df

def do_graphs(df,  pop, title, y_range, window, 
        plot_width = 300, plot_height = 300):
    df['deaths_million'] = df['deaths'] /(pop/1e6) 
    y = df['deaths_million'].rolling(window).mean()
    p = common.incidents_over_time_bar2(x = df['date'], y= y, 
            title = title,
            y_range = y_range, plot_height = plot_height, plot_width = plot_width,
            y_axis_label = 'deaths/million')
    return p

def get_html(date, script, div, window):
    """
    Create the HTML 
    """
    t = ENV.get_template('sweden_vs.j2')
    return t.render(page_title = "Sweden Vs. Other",
            script = script,
            date = date,
            page_class_attr = ["swedenComparison"],
            div = div,
            graph_title = 'Deaths per million ({w} day rolling mean)'.format(
                w = window
                ),
            )


def make_comparisons_index_html():
    """
    Create the HTML for the /comparisons/ index page
    """
    t = ENV.get_template('comparisons_index.j2')
    html = t.render(page_title = "Comparisons",
            page_class_attr = ["comparisons"],
            )
    with open(os.path.join('html_temp', 'comparisons', 'index.html'), 'w') as write_obj:
            write_obj.write(html)



def make_sweden_graph(plot_width = 300, plot_height = 300, window = 3):
    pathlib.Path("html_temp/comparisons").mkdir(parents=True, exist_ok=True)
    pops = {   'belgium': 11460000.0,
    'norway': 5368000.0,
    'ny': 19450000.0,
    'sweden': 10230000.0,
    'washington': 7615000.0}
    if not os.path.isdir('html_temp'):
        os.mkdir('html_temp')
    date = datetime.datetime.now()
    df = get_data()
    df_sweden = df[(df.region == 'Sweden') & (df.deaths > 0)]
    df_norway = df[(df.region == 'Norway') & (df.deaths > 0)]
    df_ny = df[(df.region == 'New York') & (df.deaths > 0)]
    df_belgium = df[(df.region == 'Belgium') & (df.deaths > 0)]
    df_seattle = df[(df.region == 'Seattle') & (df.deaths > 0)]
    df_washington = df[(df.region == 'Washington') & (df.deaths > 0)]
    l = []
    for i in [
            (df_sweden, 'sweden', 'Sweden', (0,15)),
            (df_norway, 'norway', 'Norway', (0,15)),
            (df_washington, 'washington', 'Washington', (0,15)),
            (df_sweden, 'sweden', 'Sweden', (0,60)),
            (df_belgium, 'belgium', 'Belgium', (0,60)),
            (df_ny, 'ny', 'New York', (0,60)),
            ]:
        l.append(do_graphs(df = i[0],  pop = pops[i[1]], title =i[2],
            plot_width = plot_width, plot_height = plot_height, y_range = i[3], 
            window = window))
    grid = gridplot(l, ncols = 3)
    script, div = components(grid)
    html = get_html(script = script, div = div,
                date = date, window = window)
    with open(os.path.join('html_temp', 'comparisons', 'sweden'), 'w') as write_obj:
            write_obj.write(html)
    make_comparisons_index_html()

if __name__ == '__main__':
    make_sweden_graph()
