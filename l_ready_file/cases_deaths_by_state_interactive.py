# pandas for data manipulation
# privde checkbox to select
# use nested function to take advantage of sharing variales
# 'date' in HoverTool is not working here
# plot tile is not working here

import time
import datetime
import pandas as pd
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import (HoverTool, ColumnDataSource, DatetimeTickFormatter)
from bokeh.models.widgets import (CheckboxGroup, Select)
from bokeh.layouts import column, row


# Make plot for cases/deaths (cds) with vbar and display in curdoc
def vbar_tab(cds):

    # Function to make a dataset for vbars based on a list of states
    def make_dataset(cds, states):
        # Iterate through all the states
        for i, state in enumerate(states):
            # Subset to the state
            cds_states = cds[cds['state'] == state]

        return ColumnDataSource(cds_states)

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

        return p

    def make_plot(source):
        # Blank plot with correct labels
        p = figure(plot_width=700,
                   plot_height=700,
                   title="Daily cases and deaths in {state} State".format(
                       state="Washington"),
                   x_axis_label='Date',
                   y_axis_label='Daily new cases & deaths')

        p.vbar(x='date',
               top='daily_cases',
               bottom=-10,
               source=source,
               line_width=3,
               width=datetime.timedelta(days=0.5),
               color='blue',
               legend_label='daily_cases')

        p.vbar(x='date',
               top='daily_deaths',
               bottom=-10,
               source=source,
               line_width=3,
               width=datetime.timedelta(days=0.5),
               color='red',
               legend_label='daily_deaths')

        p.xaxis.formatter = DatetimeTickFormatter(days=['%m/%d', '%a%d%y'])
        p.legend.location = 'top_left'
        p.xgrid.grid_line_color = None
        p.add_tools(
            HoverTool(tooltips=[('date', '@ToolTipDates'),
                                ('daily_cases', '@daily_cases'),
                                ('daily_deaths', '@daily_deaths')],
                      mode='vline'))

        p.legend.label_text_font_size = '8pt'

        return p

        # Styling
        p = style(p)

        return p

    def update(attr, old, new):
        states_to_plot = [
            state_selection.labels[i] for i in state_selection.active
        ]
        new_source = make_dataset(cds, states_to_plot)

        source.data.update(new_source.data)

    # A list of states
    states = list(set(cds['state']))
    states.sort()

    state_selection = CheckboxGroup(labels=states, active=[3, 4])
    state_selection.on_change('active', update)
    show(state_selection)

    # Initial states and data source
    initial_states = [
        state_selection.labels[i] for i in state_selection.active
    ]

    source = make_dataset(cds, initial_states)
    p = make_plot(source)

    # Put controls in a single element
    controls = column(state_selection)

    # Create a row layout
    layout = row(controls, p)

    # Put the layout in the current document for display
    curdoc().add_root(layout)


# All state data
cds = pd.read_csv(
    "/home/lizhi/projects/covid19/lizzie_covid19/state_cases_deaths.csv",
    usecols=['state', 'date', 'daily_cases', 'daily_deaths'],
    # Intepret the 'date' column as a date
    parse_dates=['date'],
    # Parse cases,deaths,daily_cases,daily_deaths columns as an integer
    dtype={('daily_deaths', 'daily_cases'): int})

vbar_tab(cds)
