import csv
import os
from google.cloud import bigquery
import datetime
import tempfile
import pprint
pp = pprint.PrettyPrinter(indent = 4)

from scipy.stats import poisson


def get_state_sql_day():
    return  """
    /* STATE BY DAY */
  SELECT  date, state, new_cases as cases, new_deaths as deaths
FROM `paul-henry-tremblay.covid19.us_states_day_diff`
order by date
  """

def get_county_sql_day():
    return  """
    /* COUNTY BY DAY */
  SELECT  date, state, county, new_cases as cases, new_deaths as deaths
FROM `paul-henry-tremblay.covid19.us_counties_diff`
order by date
  """

def get_state_data(client):
    sql = get_state_sql_day()
    fh, path = tempfile.mkstemp()
    gen_writer(client = client, sql = sql, path = path)
    return fh, path

def get_county_data(client):
    sql = get_county_sql_day()
    fh, path = tempfile.mkstemp()
    gen_writer(client = client, sql = sql, path = path)
    return fh, path

def gen_writer(client, sql, path):
    result = client.query(sql)
    with open(os.path.join('data', path), 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        counter = 0
        for i in result:
            counter += 1
            if counter == 1:
                csv_writer.writerow([x[0] for x in i.items()])
            csv_writer.writerow([x[1] for x in i.items()])

def get_poisson_for_day(date, cases, loc = 2):
    """
    Calculate when the infections occurred for a single day
    """
    final = []
    for i in range(14):
        p = poisson.pmf(i, 5, loc = loc)
        final.append((date, p * cases))
        date -= datetime.timedelta(days = 1)
    return final

def get_poisson_for_all_days(dates, cases):
    temp_dict = {}
    for i in range(len(cases)):
        p_data =  get_poisson_for_day(dates[i], cases[i])
        data = {}
        for i in p_data:
            data[i[0]] = i[1]
        for key in data.keys():
            if not temp_dict.get(key):
                temp_dict[key] = data[key]
            else:
                temp_dict[key] += data[key]
    final = []
    for key in sorted(temp_dict.keys()):
        final.append((key, temp_dict[key]))
    return final

def gen_poission(path, out_path, the_type = 'state'):
    d = {}
    with open(path, 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        counter = 0
        for row in csv_reader:
            counter += 1
            if counter == 1:
                continue
            if the_type == 'state':
                key = row[1]
            else:
                key = (row[1], row[2])
            if not d.get(key):
                d[key] = []
            if the_type == 'state':
                d[key].append([datetime.datetime.strptime(row[0], '%Y-%m-%d'),
                    int(row[2]), int(row[3])])
            else:
                d[key].append([datetime.datetime.strptime(row[0], '%Y-%m-%d'),
                    int(row[3]), int(row[4])])
    with open(out_path, 'w') as write_obj:
        csv_writer = csv.writer(write_obj)
        if the_type == 'state':
            csv_writer.writerow(['state', 'date', 'cases'])
        else:
            csv_writer.writerow(['state', 'county', 'date', 'cases'])
        for key in d.keys():
            data = sorted(d[key])
            p_data = get_poisson_for_all_days(dates = [x[0] for x in data], 
                    cases = [x[1] for x in data])[:-14]
            for i in p_data:
                if the_type == 'state':
                    csv_writer.writerow([key, i[0].strftime('%Y-%m-%d'), i[1]])
                else:
                    csv_writer.writerow([key[0], key[1], i[0].strftime('%Y-%m-%d'), i[1]])
def main(client = None):
    if not client:
        client = bigquery.Client(project='paul-henry-tremblay')
    for i in ['state', 'county']:
        if i == 'state':
            fh, temp_path =  get_state_data(client)
            gen_poission(temp_path, out_path = 'data/state_poisson.csv', the_type = i)
        else:
            fh, temp_path =  get_county_data(client)
            gen_poission(temp_path, out_path = 'data/county_poisson.csv', the_type = i)
        os.close(fh)
        os.remove(temp_path)

if __name__ == '__main__':
    main()
