#!/usr/bin/env python
# coding: utf-8

# In[12]:

import os
import datetime
import time
from google.cloud import bigquery  # This is for running sql to get the data
import pandas as pd  # Load the Pandas libraries with alias 'pd'
import math
import numpy as np
from bokeh.io import output_notebook
from bokeh.plotting import figure, show, curdoc
from bokeh.models import (CategoricalColorMapper, HoverTool, ColumnDataSource,
                          Panel, DatetimeTickFormatter, FuncTickFormatter,
                          SingleIntervalTicker, LinearAxis, Range1d)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider, Tabs,
                                  Dropdown, CheckboxButtonGroup, TableColumn,
                                  DataTable, Select, MultiSelect)
from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_20


def get_all_state_data():
    cd = pd.read_csv(
        "state_cases_deaths.csv",
        head=0,
        names=['state', 'date', 'daily_cases', 'daily_deaths'],
        # Intepret the 'date' column as a date
        parse_dates=['date'],
        # Parse cases,deaths,daily_cases,daily_deaths columns as an integer
        dtype={('cases', 'deaths', 'daily_cases', 'daily_deaths'): int})
    return cd


# Make plot with line and return tab
def line_tab(cd):
    # Prepare ColumnDataSource for individual state
    def make_state_data(state):
        cd_by_state = pd.DataFrame(
            columns=['state', 'date', 'daily_cases', 'daily_deaths'])

        cd_by_state = cd[cd['state']]
        cd_by_state['date'] = pd.to_datetime(cd_by_state['date'])
        cd_by_state['ToolTipDate'] = cd_by_state['date'].map(
            lambda x: x.strftime("%b %d"))
        return ColumnDataSource(cd_by_state)

    def style(p):
        # Title
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'

        # Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'

        # Tick formatter
        p.xaxis.formatter = DatetimeTickFormatter(days=['%m/%d', '%a%d%y'])

        return p

    # Make plot for single state
    def make_state_plot(src):
        # Blank plot with correct labels
        p = figure(plot_height=600,
                   plot_width=600,
                   x_axis_label="Date",
                   y_axis_label="Daily new cases and deaths",
                   toolbar_location="right")

        #  if max_y is not None:
        #     p.y_range = Range1d(0, max_y)

        p.line(source=src,
               x='date',
               y='daily_cases',
               line_width=2,
               color='blue',
               legend_label='daily_cases')
        p.line(source=src,
               x='date',
               y='daily_deaths',
               line_width=3,
               color='red',
               legend_label='daily_deaths')

        # Hover tool with vline mode
        p.add_tools(
            HoverTool(tooltips=[('date', '@ToolTipDates'),
                                ('daily_cases', '@daily_cases'),
                                ('daily_deaths', '@daily_deaths')],
                      mode='vline'))

        # Styling p and return
        return style(p)

    # Make plots for a grid of states
    def make_states_plots(src):
        selected_states = [
            state_selection.labels[i] for i in state_selection.active
        ]

        state_plots = []
        for state in selected_states:
            p = make_state_plot(src)
            state_plots.append(p)

    src = make_state_data(initial_states)

    src = make_state_data(initial_states)

    def update(attr, old, new):
        # Get a list of state to plot
        states_to_plot = [
            state_selection.labels[i] for i in state_selection.active
        ]

        # new_src = make_state_data(state)
        # src.data.update(new_src.data)

        print(states_to_plot)
        #print(multi_select.value)


# Read data from file 'state_cases_deaths.csv' into DataFrame
#(If the csv file is stored in the same directory that python process is based,use Relative path)
# Load file with relative path
#data = pd.read_csv("state_cases_deaths.csv")

# (If the csv file is not stored in the same directory that python process is based, use the Absolute path)
# Load  the file with Absolute path
# dir_path='/home/lizhi/projects/covid19/lizzie_covid19'
# file_name='state_cases_deaths.csv'
# csv=os.path.join(dir_path,file_name)
# data=pd.read_csv(csv)
# OR as: data=pd.read_csv('/home/lizhi/projects/covid19/lizzie_covid19/state_cases_deaths.csv')

# Read data from file 'state_cases_deaths.csv' into DataFrame with multiple parsing.
# df = pd.read_csv(
#    "state_cases_deaths.csv",
#    # Intepret the 'date' column as a date
#    parse_dates=['date'],
#    # Parse 'cases,deaths,daily_cases,daily_deaths columns as an integer
#    dtype={('cases', 'deaths', 'daily_cases', 'daily_deaths'): int})

# states and colours

    state_lst = sorted(list(set(cd['state'])))
    state_lst.sort()

    state_colours = Category20_20
    state_colours.sort()

    # Create the checkbox selection of state in state_lst
    state_selection = CheckboxGroup(labels=state_lst, active=[0, 1])
    state_selection.on_change('active', update)

    # Multiselect items in dropdown list
    # multi_select = MultiSelect(title="Select state(s):",
    #                            value=['Alabama'],
    #                            options=[x for x in zip(state_lst, state_lst)])

    #multi_select.on_change('value', update)

    # Initial state and data source
    initial_states = [
        state_selection.labels[i] for i in state_selection.active
    ]

    src = make_state_data(initial_states)
    p = make_state_plot(src)

    # Put controls in a single element
    controls = WidgetBox(state_selection)

    curdoc().add_root(column(state_selection))

    # Create a row layout
    layout = row(controls, p)

    # Make a tab with the layout
    tab = Panel(child=layout, title='Line')

    return tab
    # menu = [x for x in zip(state_lst, state_lst)]
    # dropdown = Dropdown(label="Choose State", button_type="warning", menu=menu)
    # dropdown.on_change('value', update)
