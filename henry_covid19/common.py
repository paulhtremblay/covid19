import math

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
