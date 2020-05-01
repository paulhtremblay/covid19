import datetime
from google.cloud import bigquery
import pandas as pd
import math
import numpy as np

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

def make_dataframe(l, us= False):
    d = {}
    d['dates'] = [x[0] for x in l]
    if us:
        d['cases'] = [x[1] for x in l]
        d['deaths'] = [x[2] for x in l]
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
