import datetime
from google.cloud import bigquery
import pandas as pd
import math
import numpy as np
from bokeh.plotting import figure

def tidy_name(s):
    return s.replace(' ', '_').lower()

def get_days_less_than_0(l):
    n = 1
    for i in range(len(l)):
        ind = len(l) - i - 1
        if l[ind] < 1:
            n+= 1
        else:
            return n

def get_double_rate(b):
  if b == 1:
    return 0
  x = math.log(2)/math.log(b)
  if math.isnan(x):
    return x
  return round(x, 2)

def double_rate_line(start,  rate, the_len, base = 2):
  # rate is the amount of time it takes to double
  l = []
  for i in range(the_len):
    l.append(start * math.pow(base, ((i + 1)/rate)))
  return l

def make_dataframe(l, us= False, country = False):
    d = {}
    d['dates'] = [x[0] for x in l]
    if us:
        d['cases'] = [x[1] for x in l]
        d['deaths'] = [x[2] for x in l]
    elif country:
      d['country'] = [x[1] for x in l]
      d['cases'] = [x[2] for x in l]
      d['deaths'] = [x[3] for x in l]
    else: 
      d['state'] = [x[1] for x in l]
      d['cases'] = [x[2] for x in l]
      d['deaths'] = [x[3] for x in l]
    df = pd.DataFrame.from_dict(d)
    return df

def get_state_data():
  sql = """SELECT date, state, cases, deaths FROM `paul-henry-tremblay.covid19.us_states`
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

def get_dates_extended(dates, max_date):
    dates_extended = []
    for i in dates:
      dates_extended.append(i)
    while 1:
        new_date = dates_extended[-1] + datetime.timedelta(days =1)
        dates_extended.append(new_date)
        if dates_extended[-1] == max_date.date():
          break
    dates_ = []
    for i in dates_extended:
        j = datetime.datetime(i.year, i.month, i.day)
        dates_.append(j)
    return dates_


def log_func(t, r, c, a):
  # real initial is  c / (1 + a) = 1
  return c / (1 + a * np.exp(-r * t))

def make_log_fit(df):
  deaths = df['deaths']
  x = range(1, len(deaths) + 1)
  popt, pcov = optim.curve_fit(f = log_func, xdata =x, ydata = deaths )
  return popt, pcov

def get_rate_increase(df, key, window):
  final = []
  y = df[key].rolling(window).mean().tolist()
  for counter, i in enumerate(y):
    if counter == 0:
      final.append(np.nan)
    else:
      final.append(i/y[counter - 1])
  return final

def get_rt(incidents, window, space):
    if isinstance(incidents, list):
        incidents = pd.Series(incidents)
    l = incidents.rolling(window).mean()
    if len(l) < space:
        return
    if l[-1 * space] == 0:
        return
    return l[-1]/l[-1 * space]

def bar_over_time(df, key, plot_height = 600, 
             plot_width = 600, title = None, line_width = 5, 
             ignore_last = False):
    labels = df['dates'].tolist()
    if ignore_last:
        labels = labels[0:-1]
    if isinstance(labels[0], datetime.date):
        labels = [datetime.datetime(x.year, x.month, x.day) for x in labels]
    nums = df[key].tolist()
    if ignore_last:
        nums = nums[0:-1]
    p = figure(x_axis_type = 'datetime', title = title, 
                 plot_width = plot_width , plot_height = plot_height)
    p.vbar(x=labels, top=nums, line_width = line_width, width = .9)
    return p


def incidents_over_time_bar(df, key, window= 3, plot_height = 600, 
             plot_width = 600, title = None, line_width = 5):
    labels = df['dates'].tolist()
    if isinstance(labels[0], datetime.date):
        labels = [datetime.datetime(x.year, x.month, x.day) for x in labels]
    nums = df[key].rolling(window).mean()
    p = figure(x_axis_type = 'datetime', title = title, 
                 plot_width = plot_width , plot_height = plot_height)
    p.vbar(x=labels, top=nums, line_width = line_width, width = .9)
    return p

def graph_stacked(data, title = None, start = 3, 
        plot_height = 450,line_width = 10, plot_width = 450,
        colors = ['blue', 'green', 'red', 'orange']
        ):
    if type(data['dates'][0]) == type(datetime.datetime(2020, 1, 1).date()):
        data['dates'] = [datetime.datetime(x.year, x.month, x.day) for x in data['dates']]
    labels = list(data.keys())
    del(labels[labels.index('dates')])
    colors = colors[0:len(labels) ]
    p = figure( plot_height=plot_height, title=title,
           x_axis_type= 'datetime', plot_width = plot_width)

    r = p.vbar_stack(labels, x='dates', width=1, color=colors, source=data,
             legend_label=labels, line_width = line_width)

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "top_left"
    p.legend.orientation = "vertical"
    p.legend.glyph_height = 1
    p.legend.glyph_width= 1
    p.legend.spacing  = 30
    p.legend.label_standoff = 30
    return p


def graph_wash_county_order(df, start = 3, plot_height = 450,line_width = 10):
  weeks = df['dates'][start:-1]
  years = ["King", "Snohomish", "Other"]
  colors = ["blue", "orange", "green"]
  data = {'weeks' : weeks,
        'King'   : df['king'].tolist()[start:-1],
        'Snohomish'   : df['snohomish'].tolist()[start:-1],
        'Other':df['other'].tolist()[start:-1],
        }
  p = figure( plot_height=plot_height, title="Covid19 Deaths Washington",
           x_axis_type= 'datetime')

  r = p.vbar_stack(years, x='weeks', width=1, color=colors, source=data,
             legend_label=years, line_width = line_width)

  p.y_range.start = 0
  p.x_range.range_padding = 0.1
  p.xgrid.grid_line_color = None
  p.axis.minor_tick_line_color = None
  p.outline_line_color = None
  p.legend.location = "top_left"
  p.legend.orientation = "vertical"
  p.legend.glyph_height = 1
  p.legend.glyph_width= 1
  p.legend.spacing  = 30
  p.legend.label_standoff = 30
  return p

