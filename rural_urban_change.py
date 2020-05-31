import datetime
from google.cloud import bigquery
# from matplotlib.pyplot import plot_date, axis, show, gcf, bar
import matplotlib.pyplot as plt

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.layouts import gridplot
import pprint
pp =pprint.PrettyPrinter(indent = 4)

def get_data2():
    sql = """
        select
            t3.date,
            t3.state,
            t3.county,
            t3.ru_code,
            t3.daily_cases,
            t3.daily_deaths,
            round(t3.daily_cases/t3.population *100000,2) as daily_cases_per_100k_people,
            round(t3.daily_deaths/t3.population *100000,2) as daily_deaths_per_100k_people

    from(

    select t1.date, t1.state,t1.county, t1.ru_code,
          t1.cases, t1.cases - lag(t1.cases) over(partition by t1.state, t1.county, t1.ru_code order by t1.date) as  daily_cases,
          t1.deaths,t1.deaths - lag(t1.deaths) over(partition by t1.state, t1.county, t1.ru_code order by t1.date) as  daily_deaths,
          t2.population
    from
    (select c.date, c.state, c.county, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code,
           sum(c.cases) as cases, sum(c.deaths) as deaths
    from covid19.us_counties as c
    join covid19.rural_urban_codes_2013 ruc
       on ruc.FIPS = c.fips
    group by c.date, c.state, ru_code, c.county
    order by c.state, ru_code, c.date) as t1
    join covid19.state_conversion as sc
       on sc.state_long = t1.state
    join
    (
    select state, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code, sum(population_2010) as population
    from covid19.rural_urban_codes_2013 as ruc
    group by state, ru_code
    ) as t2
       on t2.state = sc.state_code
    where t1.ru_code = t2.ru_code
    and t1.state = 'Washington'
    order by state, ru_code, date
    ) t3

    order by state, ru_code, date;

    """
    data = {}
    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    for i in result:
        county = i.get('county')
        date = i.get('date')
        cases = i.get('daily_cases_per_100k_people')
        deaths = i.get('daily_deaths_per_100k_people')
        # initialize the dictionary. If the key does not exist
        # put one there
        if not data.get(county):
            data[county] = []
        # the value of the dictionary is a list of tuples [(2020-01-30, 55, 10),....]
        data[county].append((date, cases, deaths))
    return data


def get_data():

    sql = """
        select
            t3.date,
            t3.state,
            t3.ru_code,
            t3.daily_cases,
            t3.daily_deaths,
            round(t3.daily_cases/t3.population *100000,2) as daily_cases_per_100k_people,
            round(t3.daily_deaths/t3.population *100000,2) as daily_deaths_per_100k_people

    from(

    select t1.date, t1.state, t1.ru_code,
          t1.cases, t1.cases - lag(t1.cases) over(partition by t1.state, t1.ru_code order by t1.date) as  daily_cases,
          t1.deaths,t1.deaths - lag(t1.deaths) over(partition by t1.state, t1.ru_code order by t1.date) as  daily_deaths,
          t2.population
    from
    (select c.date, c.state, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code,
           sum(c.cases) as cases, sum(c.deaths) as deaths
    from covid19.us_counties as c
    join covid19.rural_urban_codes_2013 ruc
       on ruc.FIPS = c.fips
    group by c.date, c.state, ru_code
    order by c.state, ru_code, c.date) as t1
    join covid19.state_conversion as sc
       on sc.state_long = t1.state
    join
    (
    select state, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code, sum(population_2010) as population
    from covid19.rural_urban_codes_2013 as ruc
    group by state, ru_code
    ) as t2
       on t2.state = sc.state_code
    where t1.ru_code = t2.ru_code
    and t1.state = 'Washington'
    order by state, ru_code, date
    ) t3

    order by state, ru_code, date;
"""

    client = bigquery.Client(project='paul-henry-tremblay')
    result = client.query(sql)
    date_u = []
    date_r = []
    val_u = []
    val_r = []
    daily_cases_per_100k_people_u = []
    daily_cases_per_100k_people_r = []
    daily_deaths_per_100k_people_u = []
    daily_deaths_per_100k_people_r = []
    all_data = {}

    for i in result:
        date = i.get('date')
        ru_code = i.get('ru_code')
        daily_cases = i.get('daily_cases')
        daily_cases_per_100k_people = i.get('daily_cases_per_100k_people')
        daily_deaths_per_100k_people = i.get('daily_deaths_per_100k_people')
        if ru_code == "U":
            date_u.append(date)
            val_u.append(daily_cases)
            daily_cases_per_100k_people_u.append(daily_cases_per_100k_people)
            daily_deaths_per_100k_people_u.append(daily_deaths_per_100k_people)
        else:
            date_r.append(date)
            val_r.append(daily_cases)
            daily_cases_per_100k_people_r.append(daily_cases_per_100k_people)
            daily_deaths_per_100k_people_r.append(daily_deaths_per_100k_people)
    return (date_u, val_u, date_r, val_r, daily_cases_per_100k_people_u , 
            daily_cases_per_100k_people_r, daily_deaths_per_100k_people_u, 
            daily_deaths_per_100k_people_r) 


def daily_cases_graph(dates_1, val_1, dates_2, val_2):
    # plot_date(dates, daily_cases, "o", color="blue", markeredgecolor="black")
    plt.plot(dates_1, val_1, linewidth=2.0)
    plt.plot(dates_2, val_2, linewidth=2.0)
    plt.title('Rural vs Urban daily cases in Washington State')
    #plt.dates('date')
    #plt.daily_cases('daily cases')
    #plt.setp(lines, color='r', linewidth=2.0)
    #plt.figure(figsize=(200, 150))
    plt.gcf().autofmt_xdate()
    plt.show()
    plt.savefig('temp.png')

def daily_cases_graph_bokeh(dates, incidents, plot_height = 250, 
        plot_width= 250, title = None):
    #have to convert date to datetime. rather inconvenient but necessary
    dates = [datetime.datetime(x.year, x.month, x.day) for x in dates if x != None]
    p = figure(x_axis_type = 'datetime', title = title, plot_height =plot_height, 
            plot_width = plot_width) 
    p.line(x = dates, y = incidents, color = 'red')
    p.yaxis.axis_label = 'per 100k'
    return p


"""
date_u, val_u, date_r, val_r,\
    daily_cases_per_100k_people_u,\
    daily_cases_per_100k_people_r,\
    daily_deaths_per_100k_people_u,\
    daily_deaths_per_100k_people_r\
    = get_data()
daily_cases_graph(date_u, val_u, date_r, val_r)
#daily_cases_graph(date_u, daily_cases_per_100k_people_u, date_r, daily_cases_per_100k_people_r)
daily_cases_graph_bokeh(date_u, daily_cases_per_100k_people_u, date_r, daily_cases_per_100k_people_r)
"""
the_dict = get_data2()
data_king = the_dict['King']
dates =[]
for i in data_king:
    dates.append(i[0])
cases = []
for i in data_king:
    cases.append(i[1])
p_king = daily_cases_graph_bokeh(dates, cases)

data_lincoln = the_dict['Jefferson']
dates =[]
for i in data_lincoln:
    dates.append(i[0])
cases = []
for i in data_lincoln:
    cases.append(i[1])
p_lincoln = daily_cases_graph_bokeh(dates, cases)

grid = gridplot([p_king, p_lincoln], ncols = 2)
show(grid)
