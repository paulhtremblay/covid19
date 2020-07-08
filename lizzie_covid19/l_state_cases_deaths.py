#!/usr/bin/env python
# coding: utf-8

# In[20]:


import os
import datetime
import time
from google.cloud import bigquery  # This is for running sql to get the data
import pandas as pd # Load the Pandas libraries with alias 'pd' 
import math
import numpy as np
from bokeh.io import output_notebook
from bokeh.plotting import figure, show
from bokeh.models import (CategoricalColorMapper, HoverTool, ColumnDataSource,
                          Panel, DatetimeTickFormatter, FuncTickFormatter,
                          SingleIntervalTicker, LinearAxis, Range1d)
from bokeh.models.widgets import (CheckboxGroup, Slider, RangeSlider, Tabs,
                                  CheckboxButtonGroup, TableColumn, DataTable,
                                  Select)
from bokeh.layouts import gridplot, column, row, WidgetBox
from bokeh.palettes import Category20_16

# Show current working directoory
os.getcwd()

# Read data from file 'state_cases_deaths.csv' into DataFrame
  #(If the csv file is stored in the same directory that python process is based,use Relative path)
 # Load file with relative path 
#data = pd.read_csv("state_cases_deaths.csv") 

# (If the csv file is not stored in the same directory that python process is based, use the Absolute path)
# Load  the file with Absolute path
  #dir_path='/home/lizhi/projects/covid19/lizzie_covid19'
  #file_name='state_cases_deaths.csv'
  #csv=os.path.join(dir_path,file_name)
  #data=pd.read_csv(csv)
  # OR as: data=pd.read_csv('/home/lizhi/projects/covid19/lizzie_covid19/state_cases_deaths.csv')

# Read data from file 'state_cases_deaths.csv' into DataFrame with multiple parsing.
df=pd.read_csv("state_cases_deaths.csv",
                 # Intepret the 'date' column as a date
                 parse_dates=['date'],
                 # Parse 'cases,deaths,daily_cases,daily_deaths columns as an integer 
                 dtype={('cases','deaths','daily_cases','daily_deaths'): int} 
                 ) 

# Preview the first 5 lines of the loaded data 
df.head()

def make_state_graph(state, df, max_y=None):
    # Filter state
    df_state = df.loc[df['state'] == state]
    print(df_state)
         
    df_state.loc[:,'date'] = pd.to_datetime(df_state.loc[:,'date'])
   
    df_state.loc[:,'ToolTipDates'] = df_state.loc[:,'date'].map(lambda x: x.strftime("%b %d")) 
    
    source = ColumnDataSource(df_state)
    
    p = figure(plot_height=400,
               plot_width=450,
               title='Daily cases and deaths of {state} State '.format(state=state),
               x_axis_label="Date",
               y_axis_label="Daily new cases and deaths",
               toolbar_location="below")

    if max_y is not None:
        p.y_range = Range1d(0, max_y)

    p.vbar(x='date',
           top='daily_cases',
           bottom = -10,
           source = source,
           line_width=3,
           width=datetime.timedelta(days=1), 
           color='blue',
           legend_label='daily_cases')
    
    p.vbar(x='date',
           top='daily_deaths',
           bottom=-10,
           source = source,
           line_width=3,
           width=datetime.timedelta(days=1),
           color='red',
           legend_label='daily_deaths')
    
       
    p.xaxis.formatter = DatetimeTickFormatter(days=['%m/%d', '%a%d%y'])
    p.legend.location = 'top_left'
    p.xgrid.grid_line_color = None
    p.add_tools(HoverTool(tooltips=[('date', '@ToolTipDates'),
                                    ('daily_cases', '@daily_cases'),
                                    ('daily_deaths', '@daily_deaths')], mode='vline'))
       
    p.legend.label_text_font_size = '8pt'
    return p


# Plot states graphs in grid
def all_states_graph(state, df):
    # Find list of all states then sort this list.
    states = sorted(list(set(df_state['states'])))    
    
    # Filter data down to specific state.
    #df_state = df[df['state'] == state]
    df_state = df.loc[df['state'] == state]
    
    # Find the largest number of cases, exclude the none number if there are.
    # Inflating 2% of the max_cases number to make the graph more elegant.
    max_cases = max(x for x in df_state['daily_cases'] if pd.notna(x)) * 1.05

    # Populating a list of individual state graph into a grid and plot them.
    p_list = []
    for i in states:
        p_list.append(make_state_graph(state, i, df_state, max_y=max_cases))

    grid = gridplot(p_list, ncols=2)
    show(grid)
    
    


# In[ ]:





# In[ ]:





# In[ ]:




