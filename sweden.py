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
def get_data():
    path = common.get_data_path(os.path.abspath(os.path.dirname(__file__)), 'sweden_vs.csv')
    with open(path, 'r') as read_obj:
        df = pd.read_csv(read_obj)
    df['date'] = pd.to_datetime(df['date'])
    return df

def do_graphs(df,  pop, title, y_range,
        plot_width = 300, plot_height = 300):
    df['deaths_million'] = df['deaths'] / 10.2
    p = common.incidents_over_time_bar(df = df, key = 'deaths_million', 
            title = title,
            y_range = y_range, plot_height = plot_height, plot_width = plot_width)
    return p

def get_html(date, script, div):
    """
    Create the HTML 
    """
    t = ENV.get_template('sweden_vs.html')
    return t.render(title = 'Sweden Vs. Other', 
            script =  script,
            date = date,
            div = div,
            )


def make_sweden_graph(plot_width = 300, plot_height = 300):
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
    p1 = do_graphs(df = df_sweden,  pop = pops['sweden'], title ='Sweden',
        plot_width = plot_width, plot_height = plot_height, y_range = (0, 15))
    p2 = do_graphs(df = df_norway,  pop = pops['norway'], title ='Norway',
        plot_width = plot_width, plot_height = plot_height, y_range = (0, 15))
    p3 = do_graphs(df = df_washington,  pop = pops['washington'], title ='Washington',
        plot_width = plot_width, plot_height = plot_height, y_range = (0, 15))
    p4 = do_graphs(df = df_sweden,  pop = pops['sweden'], title ='Sweden',
        plot_width = plot_width, plot_height = plot_height, y_range = (0, 90))
    p5 = do_graphs(df = df_ny,  pop = pops['ny'], title ='New York',
        plot_width = plot_width, plot_height = plot_height, y_range = (0, 90))
    p6 = do_graphs(df = df_belgium,  pop = pops['belgium'], title ='Belgium',
        plot_width = plot_width, plot_height = plot_height, y_range = (0, 90))
    grid = gridplot([p1, p2, p3, p4, p5, p6], ncols = 3)
    script, div = components(grid)
    html = get_html(script = script, div = div,
                date = date)
    with open(os.path.join('html_temp', 'sweden_vs_other.html'), 'w') as write_obj:
            write_obj.write(html)

if __name__ == '__main__':
    make_sweden_graph()
