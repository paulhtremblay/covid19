import os
import datetime
import time
from google.cloud import bigquery  # This is for running sql to get the data
import pandas as pd
import itertools as it
import operator
import math
import numpy as np
from bokeh.plotting import figure, show
from bokeh.models import (CategoricalColorMapper, HoverTool, ColumnDataSource,
                          Panel, DatetimeTickFormatter, FuncTickFormatter,
                          SingleIntervalTicker, LinearAxis)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider, Tabs,
                                  CheckboxButtonGroup, TableColumn, DataTable,
                                  Select)
from bokeh.layouts import gridplot, column, row, WidgetBox
from bokeh.palettes import Category20_16


def get_data_path(dir_path, local_path, data_path='data'):
    return os.path.join(dir_path, data_path, local_path)


def tidy_name(s):
    """Replace spaces with underscores and make it all lower cases. """
    return s.replace(' ', '_').lower()


def get_days_less_than_0(lst):
    """Finds the number of trailing list entries less than 1, then the number plus 1."""
    return 1 + sum(1 for _ in it.takewhile(lambda x: x < 1, reversed(lst)))


def get_double_rate(b):
    if b == 1:
        return 0
    x = math.log(2) / math.log(b)
    if math.isnan(x):
        return x
    return round(x, 2)


def geometric_series(start, ratio, num_elem):
    """returns num_elem values from geometric_series
    that begins at start and has ratio."""

    lst = []
    for i in range(num_elem):
        lst.append(start)
        start = start * ratio
    return lst


def double_rate_line(start, rate, the_len, base=2):
    ratio = math.pow(base, 1.0 / rate)
    return geometric_series(start * ratio, ratio, the_len)


# This is for future use if can.
def make_dataframe_helper(col_specs, data_lst):
    """Constructs dataframe from list of tuples/lists."""
    dict = {}
    for col_name, idx in col_specs:
        dict[col_name] = [x[idx] for x in data_lst]
    return pd.DataFrame.from_dict(dict)


def dataframe_from_sql(col_names, sql_str):
    dict = {}
    for x in col_names:
        dict[x] = []

    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql_str)

    for rows in result:
        for x in col_names:
            dict[x].append(rows.get(x))
    # source = ColumnDataSource(df)
    return pd.DataFrame.from_dict(dict)
    # return source


def make_county_graph(state, county, df):
    df_county = df[(df['state'] == state) & (df['county'] == county)]
    df_county_dates = [
        datetime.datetime(x.year, x.month, x.day) for x in df_county['date']
    ]

    p = figure(plot_height=400,
               plot_width=400,
               title='{county} County {state} State'.format(state=state,
                                                            county=county),
               x_axis_label="Date",
               y_axis_label="Daily new cases and deaths",
               toolbar_location="right")
    p.line(x=df_county_dates,
           y=df_county['daily_cases'],
           line_width=2,
           color='blue',
           legend_label='daily_cases')
    p.line(x=df_county_dates,
           y=df_county['daily_deaths'],
           line_width=3,
           color='red',
           legend_label='daily_deaths')
    p.xaxis.formatter = DatetimeTickFormatter(days=['%m/%d', '%a%d%y'])
    p.legend.location = 'top_left'
    p.add_tools(LassoSelectTool())
    p.add_tools(
        HoverTool(tooltips=[('date', '@date'), ('daily_cases', '@daily_cases'),
                            ('daily_deaths', '@daily_deaths')],
                  mode='vline'))

    return p


# Plot counties graphs in grid
def all_counties_graph(state, df):
    df_state = df[df['state'] == state]
    counties = sorted(list(set(df_state['county'])))
    p_list = []
    for i in counties:
        p_list.append(make_county_graph(state, i, df))
    grid = gridplot(p_list, ncols=3)
    show(grid)


def list_of_state_graph(states_lst, df):
    for state in states_lst:
        all_counties_graph(state, df)
        time.sleep(1)


#def make_county_plot(src):
#    p = figure(plot_height=400,
#               plot_width=600,
#               source=source,
#              title='{county} county Washington state'.format(county=county),
#               x_axis_label="Date",
#               y_axis_label="Daily new cases",
#               toolbar_location="right")
#    p.line(x=date,
#           y=cases,
#           line_width=2,
#           color='blue',
#           legend_label='daily_cases')
#    p.line(x=date,
#           y=deaths,
#           line_width=3,
#           color='red',
#           legend_label='daily_deaths')
#    p.xaxis.formatter = DatetimeTickFormatter(days=['%m/%d', '%a%d%y'])
#    p.legend.location = 'top_left'
#    p.add_tools(
#        HoverTool(tooltips=[('date', '@date'), ('daily_cases', '@daily_cases'),
#                            ('daily_deaths', '@daily_deaths')],
#                  mode='vline'))
#
#    return p

#def update(attr, old, new):
#    # Create the checkbox selection element, available carriers is a
#    # list of all counties in the data
#    county_selection = CheckboxGroup(labels=counties, active=[0, 1])
#
#    # select counties names from the county_selection values:
#    county_selection.labels[i] for i in county_selection.active
#
#    # Update function takes  parameters
#    # Get the list of carriers for the graph
#    county_to_plot = [county_selection.labels[i] for i in county_selection.active]
#    # Make a new dataset based on the selected county and the
#    # make_dataset function defined earlier
#    new_src = make_dataset(county_to_plot)
#    src.data.update(new_src.data)
#
#    # Link a change in selected buttons to the update function
#    county_selection.on_change('active', update)
#
#    # Put controls in a single element
#    controls=WidgetBox(county_selection)
#
#    # Create a row layout
#    layout = row(controls, p)
#
#    # Make a tab with the layout
#    tab = Panel(child=layout, title='lineplot')
#    tabs = Tabs(tabs=[tab])
#
#    curdoc().add_root(tabs)

#def dropdown_graph(menu):
#    dropdown = Dropdown(label="Dropdown button",
#                        button_type="warning",
#                        menu=menu) #    show(dropdown) # # """
"""
def get_rate_increase(df, key, window):
    final = []
    y = df[key].rolling(window).mean().tolist()
    for counter, i in enumerate(y):
        if counter == 0:
            final.append(np.nan)
        else:
            final.append(i / y[counter - 1])
    return final


def get_rt(incidents, window, space):
    if isinstance(incidents, pd.core.series.Series):
        ll = incidents.tolist()
    else:
        ll = incidents
    if len(ll) < 14:
        s = None
    last_week = ll[-14:-7]
    week = ll[-7:]
    if sum(last_week) == 0 and sum(week) == 0:
        s = 0
    elif sum(last_week) == 0:
        s = None
    else:
        s = sum(week) / sum(last_week)
    if isinstance(incidents, list):
        incidents = pd.Series(incidents)
    l = incidents.rolling(window).mean().tolist()
    if len(l) < space:
        return s, None
    if l[-1 * space] == 0:
        return s, None
    return s, l[-1] / l[-1 * space]


def bar_over_time(df,
                  key,
                  plot_height=600,
                  plot_width=600,
                  title=None,
                  line_width=5,
                  ignore_last=False):
    labels = df['dates'].tolist()
    if len(labels) == 1:
        return
    if ignore_last:
        labels = labels[0:-1]
    if isinstance(labels[0], datetime.date):
        labels = [datetime.datetime(x.year, x.month, x.day) for x in labels]
    nums = df[key].tolist()
    if ignore_last:
        nums = nums[0:-1]
    p = figure(x_axis_type='datetime',
               title=title,
               plot_width=plot_width,
               plot_height=plot_height)
    p.vbar(x=labels, top=nums, line_width=line_width, width=.9)
    return p


def incidents_over_time_bar2(x,
                             y,
                             plot_height=600,
                             plot_width=600,
                             title=None,
                             line_width=5,
                             y_range=None,
                             y_axis_label=None):
    if isinstance(x, datetime.date):
        x = [datetime.datetime(x.year, x.month, x.day) for x in x]
    p = figure(x_axis_type='datetime',
               title=title,
               plot_width=plot_width,
               plot_height=plot_height,
               y_range=y_range)
    p.vbar(x=x, top=y, line_width=line_width, width=.9)
    if y_axis_label:
        p.yaxis.axis_label = y_axis_label
    return p


def incidents_over_time_bar(df,
                            key,
                            window=3,
                            plot_height=600,
                            plot_width=600,
                            title=None,
                            line_width=5,
                            y_range=None,
                            y_axis_label=None):
    labels = df['date'].tolist()
    if isinstance(labels[0], datetime.date):
        labels = [datetime.datetime(x.year, x.month, x.day) for x in labels]
    nums = df[key].rolling(window).mean()
    p = figure(x_axis_type='datetime',
               title=title,
               plot_width=plot_width,
               plot_height=plot_height,
               y_range=y_range)
    p.vbar(x=labels, top=nums, line_width=line_width, width=.9)
    if y_axis_label:
        p.yaxis.axis_label = y_axis_label
    return p


def graph_stacked(data,
                  title=None,
                  start=3,
                  plot_height=450,
                  line_width=10,
                  plot_width=450,
                  colors=['blue', 'green', 'red', 'orange']):
    if type(data['date'][0]) == type(datetime.datetime(2020, 1, 1).date()):
        data['date'] = [
            datetime.datetime(x.year, x.month, x.day) for x in data['dates']
        ]
    labels = list(data.keys())
    del (labels[labels.index('date')])
    colors = colors[0:len(labels)]
    p = figure(plot_height=plot_height,
               title=title,
               x_axis_type='datetime',
               plot_width=plot_width)

    r = p.vbar_stack(labels,
                     x='date',
                     width=1,
                     color=colors,
                     source=data,
                     legend_label=labels,
                     line_width=line_width)

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "vertical"
    p.legend.glyph_height = 1
    p.legend.glyph_width = 1
    p.legend.spacing = 10
    p.legend.label_standoff = 10
    return p"""
