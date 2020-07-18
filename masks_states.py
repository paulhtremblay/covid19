import datetime
import os

import pandas as pd

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.layouts import gridplot
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead
from bokeh.models import Label
from bokeh.models import Span
from bokeh.embed import components

from jinja2 import Environment, select_autoescape, FileSystemLoader

from slugify import slugify

ENV = Environment(
    loader=FileSystemLoader([
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'),
        os.path.join(os.path.split(os.path.abspath(__file__))[0], 'includes')
    ]),
    autoescape=select_autoescape(['html', 'xml'])
)

ENV.filters['slugify'] = slugify

def make_df(state, start_date):
    df = pd.read_csv('data/states.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['state'] == state) & (df['date'] >= start_date)]
    return df

def make_mask_graph(df, mask_start, title = None, plot_height = 450, plot_width = 450,
                   incubation_period = 5, window = 3):
    labels = df['date'].tolist()
    nums = df['cases'].rolling(window).mean()
    p = figure(x_axis_type = 'datetime', title = title, 
                 plot_width = plot_width , plot_height = plot_height, y_range = None)
    dd = list(zip(labels, nums))
    bef = [x for x in dd if x[0] <= mask_start]

    incc = [x for x in dd if x[0] >  mask_start 
        and x[0] <= mask_start + datetime.timedelta(days = incubation_period)
      ]
    aff = [x for x in dd if x[0] > mask_start + datetime.timedelta(days = incubation_period)]

    p.vbar(x=[x[0] for x in bef], top=[x[1] for x in bef] , line_width = 5, 
           width = .9, color = 'yellow', 
       )
    p.vbar(x=[x[0] for x in incc], top=[x[1] for x in incc] , line_width = 5, 
           width = .9, color = 'red', 
       )
    p.vbar(x=[x[0] for x in aff], top=[x[1] for x in aff] , line_width = 5, 
           width = .9, color = 'orange', 
       )
    #p.legend.location = "top_center"
    return p

def do_mask_mandates(window = 3, plot_height = 450, 
                    plot_width = 450, ncols = 4):
    return gridplot([
            
            make_mask_graph(df = 
                make_df(state = 'California', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,6,18),
                    title = 'California', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ),   
                
            make_mask_graph(df = 
                make_df(state = 'Connecticut', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,4,20),
                    title = 'Connecticut', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ),
            make_mask_graph(df = 
                make_df(state = 'Delaware', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,4,28),
                    title = 'Delaware', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Hawaii', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,4,20),
                    title = 'Hawaii', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Illinois', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,5,1),
                    title = 'Illinois', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Kansas', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,7,3),
                    title = 'Kansas', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Kentucky', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,5,11),
                    title = 'Kentuckky', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
             make_mask_graph(df = 
                make_df(state = 'Maine', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,5,1),
                    title = 'Maine', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ),
             make_mask_graph(df = 
                make_df(state = 'Maryland', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,4,18),
                    title = 'Maryland', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
             make_mask_graph(df = 
                make_df(state = 'Massachusetts', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,5,6),
                    title = 'Massachusetts', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Michigan', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,6,18),
                    title = 'Michigan', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Nevada', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,6,24),
                    title = 'Nevada', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ),
            make_mask_graph(df = 
                make_df(state = 'New Jersey', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,4,8),
                    title = 'New Jersey', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ),
            make_mask_graph(df = 
                make_df(state = 'New Mexico', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,5,16),
                    title = 'New Mexico', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
             make_mask_graph(df = 
                make_df(state = 'New York', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,4,17),
                    title = 'New York', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ),
            make_mask_graph(df = 
                make_df(state = 'North Carolina', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,6,26),
                    title = 'North Corolina', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Oregon', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,7,1),
                    title = 'Oregeon', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Pennsylvania', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,4,19),
                    title = 'Pennsylvania', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ),
             make_mask_graph(df = 
                make_df(state = 'Rhode Island', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,5,18),
                    title = 'Rhode Island', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
             make_mask_graph(df = 
                make_df(state = 'Texas', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,7,3),
                    title = 'Texas', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Virginia', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,5,29),
                    title = 'Virginia', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'Washington', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,6,26),
                    title = 'Washington', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
            make_mask_graph(df = 
                make_df(state = 'West Virginia', 
                        start_date = datetime.datetime(2020,4, 1)),
                mask_start = datetime.datetime(2020,7,6),
                    title = 'West Virginia', plot_height = plot_height,
                                     plot_width = plot_width,
                            window = window,
               ), 
         ], 
         
         
         ncols = ncols)

def get_html(script, div):
    """
    Create the HTML  
    """
    t = ENV.get_template('masks.j2')
    return t.render(
            script = script,
            div = div,
            )

def main():
    g = do_mask_mandates(window = 7, plot_height = 350, plot_width = 300)
    script, div = components(g)
    html = get_html(script=script, div=div)
    with open(os.path.join('html_temp', 'state-masks'), 'w') as write_obj:
        write_obj.write(html)

if __name__ == '__main__':
    main()

